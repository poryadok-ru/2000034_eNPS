import json
from openai import OpenAI

class AIAnalyzer:
    def __init__(self, config):
        try:
            self.client = OpenAI(api_key=config["api_key"], base_url=config["base_url"])
            self.model = config["model_name"]
        except Exception as e:
            raise e

    def analyze(self, submissions, context):
        if not submissions:
            return {
                "analytics": "Нет данных для анализа.",
                "recommendations": "1. Информации недостаточно.",
                "positive_feedback": "Нет данных о положительных аспектах.",
                "negative_feedback": "Нет данных о предложениях по улучшению."
            }

        # Собираем все answers для передачи ИИ
        all_answers = []
        for s in submissions:
            answers = s.get('answers')
            if answers:
                # Преобразуем answers в строку JSON если это dict
                if isinstance(answers, dict):
                    all_answers.append(json.dumps(answers, ensure_ascii=False, indent=2))
                else:
                    all_answers.append(str(answers))

        # Если нет answers, используем информацию о рейтингах
        ratings = [s.get('rating') for s in submissions]
        ratings = [r for r in ratings if r is not None]

        if not all_answers:
            sample_text = f"Рейтинги сотрудников: {ratings}"
        else:
            # Берем первые 10 answers для анализа чтобы не перегружать ИИ
            sample_answers = all_answers[:10]
            sample_text = "Ответы сотрудников (JSON формат):\n" + "\n".join(sample_answers)
            if ratings:
                sample_text += f"\n\nРейтинги сотрудников: {ratings}"

        prompt = (
            f"Ты HR-эксперт. Проведи анализ eNPS для {context} на основе следующих данных:\n"
            f"{sample_text}\n\n"
            "Верни результат в JSON формате со следующими полями:\n"
            "1. \"Аналитика\" - Приведи общий анализ ситуации с вовлеченностью сотрудников\n"
            "2. \"Рекомендации\" - Приведи не более 5 конкретных, рекомендаций по улучшению eNPS и по решению проблем исходя из анализа\n"
            "3. \"Что_нравится\" - Перечисли основные положительные моменты, которые отмечают сотрудники, с примерами некоторых ярких комментариев сотрудников\n"
            "4. \"Что_улучшить\" - перечисли основные проблемы и предложения по улучшению от сотрудников, с примерами некоторых ярких комментариев сотрудников\n"
            "Формат: {\"Аналитика\": \"...\", \"Рекомендации\": \"1. ...\\n2. ...\", \"Что_нравится\": \"...\", \"Что_улучшить\": \"...\"}"
        )

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )

            data = json.loads(resp.choices[0].message.content)

            return {
                "analytics": data.get("Аналитика", "Анализ не удался"),
                "recommendations": data.get("Рекомендации", "1. Нет данных для анализа"),
                "positive_feedback": data.get("Что_нравится", "Нет данных о положительных аспектах"),
                "negative_feedback": data.get("Что_улучшить", "Нет данных о предложениях по улучшению")
            }
        except Exception as e:
            raise e