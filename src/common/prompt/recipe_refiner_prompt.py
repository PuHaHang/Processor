"""
레시피 정제 프롬프트 모듈

이 모듈은 Gemini 모델을 사용하여 멀티미디어 데이터를 레시피로 정제하기 위한
프롬프트 템플릿들을 정의합니다.
"""

from typing import Dict, Any


class RecipeRefinerPrompt:
    """
    레시피 정제를 위한 프롬프트 템플릿 클래스
    
    다양한 데이터 타입(VIDEO, AUDIO, TEXT)에 대해 레시피 추출 및 정제를 위한
    프롬프트를 제공합니다.
    """

    @staticmethod
    def get_video_recipe_prompt() -> str:
        """
        비디오 데이터로부터 레시피를 추출하기 위한 프롬프트를 반환합니다.
        
        Returns:
            str: 비디오 레시피 추출 프롬프트
        """
        return """
당신은 요리 전문가입니다. 제공된 비디오를 분석하여 구조화된 레시피를 추출해주세요.

다음 JSON 형식으로 레시피를 작성해주세요:

```json
{
  "title": "[요리 이름]",
  "author": "[작성자]",
  "ingredients": [
    {
      "index": 1,
      "name": "[재료명]",
      "amount": "[분량]",
      "unit": "[단위, 없으면 비워둠]"
    },
    {
      "index": 2,
      "name": "[재료명]",
      "amount": "[분량]",
      "unit": "[단위, 없으면 비워둠]"
    }
  ],
  "stages": [
    {
      "step": 1,
      "start_time": "**.**",
      "end_time": "**.**",
      "description": "[조리 과정 설명]"
    },
    {
      "step": 2,
      "start_time": "**.**",
      "end_time": "**.**",
      "description": "[조리 과정 설명]"
    }
  ],
  "estimated_time": "[시간]",
  "difficulty": "[초급/중급/고급]",
  "servings": "[제공인분]"
}
```

비디오에서 보이는 모든 조리 과정을 단계별로 상세히 기록하고, 재료의 정확한 분량과 조리 시간을 명시해주세요.
조리 시간은 초 단위로 표시해주세요.
언급된 재료는 재료 목록에 포함시키며 조리 과정에서는 재료와 분량을 {재료 순번}으로만 표시해주세요.
조리 과정에서 표시된 재료 순번은 재료 목록에 있는 재료 순번과 동일해야 하며 {1}, {2}, {3} 형식으로 표시해주세요.
단위는 단위 표시 외에는 작성하지 마세요. 단위가 없는 경우 비워두세요.
"""

    @staticmethod
    def get_audio_recipe_prompt() -> str:
        """
        오디오 데이터로부터 레시피를 추출하기 위한 프롬프트를 반환합니다.
        
        Returns:
            str: 오디오 레시피 추출 프롬프트
        """
        return """
당신은 요리 전문가입니다. 제공된 오디오를 분석하여 구조화된 레시피를 추출해주세요.

다음 JSON 형식으로 레시피를 작성해주세요:

```json
{
  "title": "[요리 이름]",
  "author": "[작성자]",
  "ingredients": [
    {
      "index": 1,
      "name": "[재료명]",
      "amount": "[분량]",
      "unit": "[단위, 없으면 비워둠]"
    },
    {
      "index": 2,
      "name": "[재료명]",
      "amount": "[분량]",
      "unit": "[단위, 없으면 비워둠]"
    }
  ],
  "stages": [
    {
      "step": 1,
      "start_time": "**.**",
      "end_time": "**.**",
      "description": "[조리 과정 설명]"
    },
    {
      "step": 2,
      "start_time": "**.**",
      "end_time": "**.**",
      "description": "[조리 과정 설명]"
    }
  ],
  "estimated_time": "[시간]",
  "difficulty": "[초급/중급/고급]",
  "servings": "[제공인분]"
}
```

오디오에서 들리는 모든 설명을 바탕으로 조리 과정을 단계별로 상세히 기록하고,
언급된 재료의 분량과 조리 시간을 정확히 파악해주세요.
조리 시간은 초 단위로 표시해주세요.
언급된 재료는 재료 목록에 포함시키며 조리 과정에서는 재료와 분량을 {재료 순번}으로만 표시해주세요.
조리 과정에서 표시된 재료 순번은 재료 목록에 있는 재료 순번과 동일해야 하며 {1}, {2}, {3} 형식으로 표시해주세요.
단위는 단위 표시 외에는 작성하지 마세요. 단위가 없는 경우 비워두세요.
"""

    @staticmethod
    def get_text_recipe_prompt(language: str = "ko") -> str:
        """
        텍스트 데이터로부터 레시피를 정제하기 위한 프롬프트를 반환합니다.
        
        Returns:
            str: 텍스트 레시피 정제 프롬프트
        """
        return f"""
당신은 요리 전문가입니다. 제공된 transcript 텍스트를 분석하여 구조화된 레시피로 정제해주세요.

다음 JSON 형식으로 레시피를 작성해주세요:

```json
{{
  "title": "[요리 이름]",
  "author": "[작성자]",
  "ingredients": [
    {{
      "index": 1,
      "name": "[재료명]",
      "amount": "[분량]",
      "unit": "[단위, 없으면 비워둠]"
    }},
    {{
      "index": 2,
      "name": "[재료명]",
      "amount": "[분량]",
      "unit": "[단위, 없으면 비워둠]"
    }}
  ],
  "stages": [
    {{
      "step": 1,
      "start_time": "**.**",
      "end_time": "**.**",
      "description": "[조리 과정 설명]"
    }},
    {{
      "step": 2,
      "start_time": "**.**",
      "end_time": "**.**",
      "description": "[조리 과정 설명]"
    }}
  ],
  "estimated_time": "[시간]",
  "difficulty": "[초급/중급/고급]",
  "servings": "[제공인분]"
}}
```

제공된 텍스트가 불완전하거나 부정확한 정보를 포함할 수 있습니다.
전문 지식을 바탕으로 누락된 정보를 보완하고, 정확하고 실용적인 레시피로 정제해주세요.
조리 시간은 초 단위로 표시해주세요.
언급된 재료는 재료 목록에 포함시키며 조리 과정에서는 재료와 분량을 {{재료 순번}}으로만 표시해주세요.
조리 과정에서 표시된 재료 순번은 재료 목록에 있는 재료 순번과 동일해야 하며 {{1}}, {{2}}, {{3}} 형식으로 표시해주세요.
단위는 단위 표시 외에는 작성하지 마세요. 단위가 없는 경우 비워두세요.
[문자열]은 주어진 컨텐츠의 언어에 관계없이 언어 코드:{language}에 해당하는 언어로 작성해주세요.
"""

    @staticmethod
    def get_content_context_prompt(metadata: Dict[str, Any]) -> str:
        """
        메타데이터를 바탕으로 컨텍스트 정보를 생성합니다.
        
        Args:
            metadata (Dict[str, Any]): 페이로드 메타데이터
            
        Returns:
            str: 컨텍스트 정보가 포함된 프롬프트
        """
        context = ""
        if metadata:
            context += f"- 메타데이터:\n{metadata}\n"
            
        if context:
            return f"**컨텍스트 정보:**\n{context}\n"
        
        return "" 
    
    @staticmethod
    def get_recipe_prompt_format() -> str:
        """
        레시피 정제를 위한 프롬프트를 반환합니다.
        """
        return """
다음 JSON 형식으로 레시피를 작성해주세요:
```json
{
  "title": "비프 웰링턴 (Beef Wellington)",
  "author": "John Doe",
  "ingredients": [
    {
      "index": 1,
      "name": "소고기 안심 (필레)",
      "amount": "1.2",
      "unit": "kg"
    },
    {
      "index": 2,
      "name": "소금",
      "amount": "적당히",
      "unit": ""
    },
    {
      "index": 3,
      "name": "후추",
      "amount": "적당히",
      "unit": ""
    },
    {
      "index": 4,
      "name": "올리브 오일",
      "amount": "2",
      "unit": "큰술"
    },
    {
      "index": 5,
      "name": "잉글리시 머스타드",
      "amount": "2",
      "unit": "큰술"
    },
    {
      "index": 6,
      "name": "밤버섯 (또는 양송이버섯)",
      "amount": "700",
      "unit": "g"
    },
    {
      "index": 7,
      "name": "마늘",
      "amount": "1",
      "unit": "쪽"
    },
    {
      "index": 8,
      "name": "소금",
      "amount": "1",
      "unit": "큰술"
    },
    {
      "index": 9,
      "name": "후추",
      "amount": "1",
      "unit": "큰술"
    },
    {
      "index": 10,
      "name": "삶은 밤",
      "amount": "200",
      "unit": "g"
    },
    {
      "index": 11,
      "name": "신선한 타임",
      "amount": "1",
      "unit": "작은술"
    },
    {
      "index": 12,
      "name": "프로슈토 (파르마 햄)",
      "amount": "10",
      "unit": "장"
    },
    {
      "index": 13,
      "name": "퍼프 페이스트리 시트",
      "amount": "1",
      "unit": "장"
    },
    {
      "index": 14,
      "name": "달걀 노른자",
      "amount": "1",
      "unit": "개"
    },
    {
      "index": 15,
      "name": "굵은 소금",
      "amount": "1",
      "unit": "큰술"
    }
  ],
  "stages": [
    {
      "step": 1,
      "start_time": "18.559",
      "end_time": "70.320",
      "description": "{1}에 {2}와 {3}을 골고루 뿌려 밑간한다. 아주 뜨겁게 달군 팬에 {4}를 두른 후, 밑간한 {1}을 넣고 모든 면이 갈색이 될 때까지 빠르게 지진다. (소고기를 익히는 것이 아니라 표면을 캐러멜화하여 풍미를 더하는 과정이다.)"
    },
    {
      "step": 2,
      "start_time": "70.320",
      "end_time": "97.279",
      "description": "팬에서 꺼낸 뜨거운 {1}의 모든 표면에 {5}를 골고루 바른다. 잠시 그대로 두어 {1}이 식으면서 머스타드의 풍미를 흡수하고 육즙이 재분배되도록 한다."
    },
    {
      "step": 3,
      "start_time": "101.440",
      "end_time": "120.000",
      "description": "믹서에 {6}, {7}, {2}, {3}을 넣고 곱게 간다. 여기에 {8}을 손으로 부숴 넣고 다시 한번 가볍게 간다."
    },
    {
      "step": 4,
      "start_time": "141.100",
      "end_time": "174.179",
      "description": "뜨겁게 달군 마른 팬에 간 {6}과 {8} 혼합물(둑셀)을 넣고 수분이 완전히 날아갈 때까지 볶는다. (이 과정은 웰링턴의 성공에 매우 중요하며, 버섯의 풍미를 응축시킨다.) 마지막으로 {9}를 넣고 섞은 후, 팬에서 꺼내 식힌다."
    },
    {
      "step": 5,
      "start_time": "179.220",
      "end_time": "295.739",
      "description": "랩을 넓게 펼친 후, 그 위에 {10}을 약간 겹치도록 평평하게 깔아 직사각형 모양을 만든다. {3}을 약간 뿌리고, 식힌 둑셀을 {10} 위에 얇게 펴 바른다. 중앙에 {1}을 올리고, {10}으로 {1}을 감싸듯 조심스럽게 감싼다. 랩으로 단단하게 감싸서 원통형 모양을 만든 후, 양 끝을 비틀어 고정한다."
    },
    {
      "step": 6,
      "start_time": "299.059",
      "end_time": "309.260",
      "description": "단계 5에서 준비한 {1}을 랩으로 감싼 상태 그대로 냉장고에 넣어 최소 15분간 굳힌다."
    },
    {
      "step": 7,
      "start_time": "311.459",
      "end_time": "365.660",
      "description": "냉장고에서 꺼낸 {1}을 랩에서 벗긴다. 랩을 넓게 깐 후 그 위에 {11}을 올리고, {1}을 {11}으로 감싼다. 이음새와 양 끝을 잘 봉하고 여분의 페이스트리는 잘라낸다. 다시 랩으로 단단하게 감싸서 모양을 고
    },
    {
      "step": 8,
      "start_time": "374.619",
      "end_time": "401.140",
      "description": "냉장고에서 꺼낸 {1}을 랩에서 벗긴 후, {12}를 골고루 바른다. 칼등으로 페이스트리 표면에 장식용 무늬를 내고, {13}을 넉넉하게 뿌린다."
    },
    {
      "step": 9,
      "start_time": "401.140",
      "end_time": "407.220",
      "description": "200°C로 예열된 오븐에서 35분간 굽는다. (소고기 굽기 정도에 따라 조리 시간을 조절한다.)"
    },
    {
      "step": 10,
      "start_time": "407.220",
      "end_time": "446.820",
      "description": "오븐에서 꺼낸 웰링턴을 최소 10분 이상 그대로 두어 휴지시킨다. (이 과정은 육즙을 보존하고 소고기를 부드럽고 촉촉하게 만든다.) 먹기 좋은 크기로 잘라 따뜻하게 제공한다."
    }
  ],
  "estimated_time": "약 120분",
  "difficulty": "고급",
  "servings": "4-6인분"
}
```
"""