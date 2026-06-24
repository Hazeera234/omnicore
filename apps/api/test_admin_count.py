import asyncio
from uuid import uuid4
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func
from app.models.project_member import ProjectMember

async def test():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    # We can't easily set up the whole schema here, but let's check what select(func.count()).where(...) produces
    stmt = select(func.count()).where(
        ProjectMember.project_id == uuid4(),
        ProjectMember.role == "admin"
    )
    print("SQL:", str(stmt))

asyncio.run(test())
