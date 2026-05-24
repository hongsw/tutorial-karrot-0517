"""
SESSION 4 실습 C: CrewAI로 콘텐츠 팀
사용법:
  pip install crewai
  export OPENAI_API_KEY="sk-..."   # 또는 ANTHROPIC_API_KEY
  python crew.py
"""

from crewai import Agent, Task, Crew, Process

researcher = Agent(
    role="리서처",
    goal="주어진 주제에 대해 핵심 포인트 5개와 SEO 키워드를 수집한다",
    backstory="1인 사업자를 위한 콘텐츠 전략가. 데이터 기반으로 분석한다.",
    verbose=True,
)

writer = Agent(
    role="라이터",
    goal="리서처의 결과로 SEO 최적화된 블로그 포스트 초안을 작성한다",
    backstory="B2C 스타트업 마케터 출신, 한국어 콘텐츠 전문가.",
    verbose=True,
)

critic = Agent(
    role="크리틱",
    goal="초안의 논리 흐름, 톤, SEO를 검수하고 개선점 3개를 제시한다",
    backstory="에디터 경력 10년, 독자 입장에서 냉정하게 평가한다.",
    verbose=True,
)

TOPIC = "1인 사업자가 AI로 고객 응대를 자동화하는 3가지 방법"

task_research = Task(
    description=f"주제 '{TOPIC}'를 리서치해 핵심 포인트 5개와 SEO 키워드 10개를 정리하라.",
    agent=researcher,
    expected_output="핵심 포인트 목록 + 키워드 목록",
)

task_write = Task(
    description="리서치 결과로 600자 블로그 포스트 초안을 작성하라. 소제목 3개 포함.",
    agent=writer,
    expected_output="블로그 포스트 초안 (Markdown)",
    context=[task_research],
)

task_critique = Task(
    description="초안을 검수하고 개선점 3개를 구체적으로 제시하라.",
    agent=critic,
    expected_output="개선 제안 3개 + 수정된 최종본",
    context=[task_write],
)

crew = Crew(
    agents=[researcher, writer, critic],
    tasks=[task_research, task_write, task_critique],
    process=Process.sequential,
    verbose=True,
)

if __name__ == "__main__":
    result = crew.kickoff()
    print("\n\n=== 최종 결과 ===")
    print(result)
