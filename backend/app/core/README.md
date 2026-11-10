# backend/app/core/

Cross-cutting backend code: settings loaded from environment variables (see the root `.env.example`), logging setup, shared exceptions and constants.

Never hard-code secrets here. Read them from the environment.

**Primary owners:** Toheeb + Parmeet (#3). Environment and config conventions are coordinated with Saqib + Megh (#5).
