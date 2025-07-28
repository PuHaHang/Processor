from datetime import datetime
import json
import os
import boto3
import time

from src.common.image_generation.gemini_generator import GeminiGenerator
from src.common.fcm.fcm_manager import send_notification
from src.common.rdb.domain.recipe.dto.update_recipe_base_dto import UpdateRecipeBaseDto
from src.common.rdb.domain.recipe.models import Ingredient, Recipe, RecipeDifficulty, RecipeState
from src.common.rdb.domain.recipe.recipe_base_service import RecipeBaseService
from src.common.rdb.domain.recipe.recipe_service import RecipeService
from src.common.rdb.domain.recipe.repository.ingredient_repository import IngredientRepository
from src.common.rdb.domain.user.user_service import UserService
from src.common.s3 import s3_connector

from ..common.processor.agent import Agent
from ..common.processor.types.payload import Payload
from ..common.processor.types import DataType, PayloadStatus

# AWS 세션 생성 (환경변수 또는 IAM 역할 필요)
sqs = boto3.client('sqs', region_name='ap-northeast-2')  # 서울 리전
queue_url = os.getenv("AWS_SQS_QUEUE_URL")

processor_agent = Agent()

def process_message(message):
    # 메시지 처리 로직
    try:
        print(message)
        # print(f"📩 Received message: {message['Body']}")
        json_data = json.loads(message['Body'])

        recipe_base_content_id = json_data['recipeBaseContentId']
        platform = json_data['platform']
        source = json_data['source']
        language = json_data['language']
        # user_id = json_data['user_id']
        
        if platform == "YOUTUBE":
            payload = Payload(
                buffer=source.encode('utf-8'),
                metadata={},
                data_type=DataType.URL,
                status=PayloadStatus.INIT,
                processor=None,
            )
        elif platform == "TEXT":
            payload = Payload(
                buffer=source.encode('utf-8'),
                metadata={},
                data_type=DataType.TEXT,
                status=PayloadStatus.INIT,
                processor=None,
            )

        payload = processor_agent.process(payload, int(recipe_base_content_id), language)

        payload_saver(payload, recipe_base_content_id)
        print("Payload:", payload.buffer.decode('utf-8'))
    except Exception as e:
        print(f"❌ Error while processing message: {e}")
        print(str(e))

def payload_saver(payload: Payload, recipe_base_content_id: int):
    recipe_base_service = RecipeBaseService()
    ingredient_repository = IngredientRepository()

    data = json.loads(payload.buffer)

    image_generator = GeminiGenerator()
    image_prompt = data['image_prompt']
    image = image_generator.generate_image(image_prompt)
    
    image_url = None
    try:
        image_url = s3_connector.upload_image_to_s3(image, f"recipe_images/originals/{recipe_base_content_id}.png", os.getenv("AWS_S3_BUCKET_NAME"))
    except Exception as e:
        print(f"❌ Error while uploading image to S3: {e}")
        return
    
    difficulty = RecipeDifficulty(data['difficulty'])
    try:
        estimated_time = int(data['estimated_time'])
    except Exception as e:
        estimated_time = None
    
    try:
        servings = int(data['servings'])
    except Exception as e:
        servings = None
    
    # print(data)
    with processor_agent.db_manager.session_scope() as session:
        ingredients = []
        for ingredient in data['ingredients']:
            if not ingredient_repository.exists_by_name(session, ingredient['name']):
                ingredient_entity = Ingredient(
                    ingredient=ingredient['name'],
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )
                added_ingredient = ingredient_repository.create(session, ingredient_entity)
            else:
                added_ingredient = ingredient_repository.find_by_name(session, ingredient['name'])

            ingredients.append(added_ingredient)

        for i, stage in enumerate(data['stages']):
            for j, ingredient in enumerate(ingredients):
                data['stages'][i]['description'] = data['stages'][i]['description'].replace(f"{{{j+1}}}", str(ingredient.ingredient_id))
        
        for i, ingredient in enumerate(data['ingredients']):
            ingredient.pop('index')
            ingredient['ingredient_id'] = ingredients[i].ingredient_id
            data['ingredients'][i] = ingredient
        
        recipe_base_content = recipe_base_service.get_recipe_base_content_by_id(session, recipe_base_content_id)

        recipe_base_content.title = data['title']
        recipe_base_content.author = data['author']
        recipe_base_content.ingredients = data['ingredients']
        recipe_base_content.stages = data['stages']
        recipe_base_content.updated_at = datetime.now()

        recipe_base_service.update_recipe_base_content(session, recipe_base_content)
        recipe_base_service.update_recipe_base_state(session, recipe_base_content_id, RecipeState.COMPLETED)

        recipe_base = recipe_base_service.get_recipe_base_by_id(session, recipe_base_content.recipe_base_id)
        recipe_base_service.update_recipe_base(session, UpdateRecipeBaseDto(
            recipe_base_id=recipe_base.recipe_base_id,
            difficulty=difficulty,
            estimated_time=estimated_time,
            servings=servings,
            thumbnail=image_url
        ))
    
    alert_fcm_token(recipe_base_content_id, data['title'], image_url)

def alert_fcm_token(recipe_base_content_id: int, body: str, image_url: str = ""):
    user_service = UserService()
    recipe_service = RecipeService()

    title = "새로운 레시피가 추가되었습니다."
    
    with processor_agent.db_manager.session_scope() as session:
        recipes = []
        offset = 0
        limit = 100
        
        while True:
            batch = recipe_service.get_recipes_by_base(session, recipe_base_content_id, limit=limit, offset=offset)
            if not batch:
                break
            recipes.extend(batch)
            offset += limit
        
        user_ids = [recipe.user_id for recipe in recipes]
        user_alerts = user_service.get_user_alerts_by_user_ids(session, user_ids)

        target_fcm_tokens = [user_alert.fcm_token for user_alert in user_alerts if user_alert.is_alerted]

        if not target_fcm_tokens:
            return
    
    for target_fcm_token in target_fcm_tokens:
        try:
            send_notification(
                target_fcm_token,
                title,
                body,
                image_url
            )
        except Exception as e:
            print(f"❌ Error while sending notification: {e}")
            continue

def poll_messages():
    print("👂 SQS Subscriber is running...")
    cnt = 0
    tolerance = int(os.getenv("AWS_SQS_POLL_COUNT", 3))
    if tolerance == 0:
        tolerance = 1e9
    while cnt < tolerance:
        # print(queue_url)
        try:
            # 메시지 수신 (최대 10개, 최대 20초 대기)
            response = sqs.receive_message(
                QueueUrl=queue_url,
                AttributeNames=['All'],
                MaxNumberOfMessages=int(os.getenv("AWS_SQS_MAX_NUMBER_OF_MESSAGES", 10)),
                WaitTimeSeconds=int(os.getenv("AWS_SQS_WAIT_TIME_SECONDS", 20)),  # long polling
                VisibilityTimeout=int(os.getenv("AWS_SQS_VISIBILITY_TIMEOUT", 30))  # 메시지 처리 시간
            )
        except Exception as e:
            print(f"❌ Error while polling: {e}")
            time.sleep(1)  # 재시도 전 대기
            continue
        
        cnt += 1
        if not response:
            continue

        messages = response.get('Messages', [])
        # print(messages)
        if not messages:
            continue
        cnt = 0

        target_messages = []
        for message in messages:
            try:
                sqs.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=message['ReceiptHandle']
                )
                target_messages.append(message)
            except Exception as e:
                print(f"❌ Error while deleting message: {e}")
                continue

        # print("processing messages")
        for message in target_messages:
            try:
                process_message(message)
            except Exception as e:
                print(f"❌ Error while processing message: {e}")
                sqs.send_message(
                    QueueUrl=queue_url,
                    MessageBody=message['Body'],
                    DelaySeconds=0
                )
                continue

if __name__ == "__main__":
    poll_messages()