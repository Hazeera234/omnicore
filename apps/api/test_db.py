import asyncio
from app.db.session import async_session_maker
from app.services.member_service import MemberService
from app.models.project import Project
from app.models.project_member import ProjectMember
from sqlalchemy import select, func

async def test():
    async with async_session_maker() as db:
        # get any project
        result = await db.execute(select(Project).limit(1))
        project = result.scalars().first()
        if not project:
            print("No project found")
            return
            
        print(f"Project ID: {project.project_id}")
        
        admin_count_result = await db.execute(select(func.count()).where(
            ProjectMember.project_id == project.project_id,
            ProjectMember.role == 'admin'
        ))
        print("Admin count is:", admin_count_result.scalar())
        
        # let's try calling select_from
        admin_count_result_2 = await db.execute(select(func.count(ProjectMember.user_id)).where(
            ProjectMember.project_id == project.project_id,
            ProjectMember.role == 'admin'
        ))
        print("Admin count 2 is:", admin_count_result_2.scalar())

asyncio.run(test())
