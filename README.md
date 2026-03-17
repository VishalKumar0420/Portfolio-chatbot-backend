## Folder Structure

```
app/
├── config/
│   ├── settings.py
│   ├── constants.py
│   ├── security.py
│   ├── database.py
│   ├── redis.py
│   ├── groq.py
│   └── pinecone.py
│
├── middleware/
│   └── auth.py
│
├── utils/
│   ├── call_groq_llm.py
│   ├── detect_sections.py
│   ├── normalize_text.py
│   ├── preprocess_query.py
│   └── resume_parser.py
│
├── modules/
│   ├── health/
│   │   └── router.py
│   ├── auth/
│   │   ├── model.py
│   │   ├── schema.py
│   │   ├── service.py
│   │   ├── controller.py
│   │   └── router.py
│   ├── chat/
│   │   ├── model.py
│   │   ├── schema.py
│   │   ├── service.py
│   │   ├── controller.py
│   │   └── router.py
│   └── resume/
│       ├── schema.py
│       ├── service.py
│       ├── controller.py
│       └── router.py
│
├── schemas/
│   └── common.py
├── responses.py
└── main.py
```
