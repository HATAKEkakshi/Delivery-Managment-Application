# create_tags.py - Run this once to populate your database with tags
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.model import Tag, TagName
from database.session import get_session  # Use get_session instead of get_async_session

async def create_default_tags():
    """Create all predefined tags in the database"""
    
    # Define tag instructions
    tag_instructions = {
        TagName.EXPRESS: "Priority delivery with faster processing time",
        TagName.STANDARD: "Regular delivery with standard processing time", 
        TagName.FRAGILE: "Handle with extra care - fragile contents",
        TagName.HEAVY: "Heavy package requiring special handling",
        TagName.INTERNATIONAL: "International shipment with customs requirements",
        TagName.DOMESTIC: "Domestic shipment within country",
        TagName.TEMPERATURE_CONTROLLED: "Requires temperature-controlled transportation",
        TagName.GIFT: "Gift package with special packaging",
        TagName.RETURN: "Return shipment",
        TagName.DOCUMENTS: "Document shipment - expedited processing"
    }
    
    # Use the async session generator properly
    async for session in get_session():
        try:
            # Check existing tags to avoid duplicates
            result = await session.execute(select(Tag))
            existing_tags = result.scalars().all()
            existing_tag_names = {tag.name for tag in existing_tags}
            
            new_tags = []
            for tag_name in TagName:
                if tag_name.value not in existing_tag_names:
                    new_tag = Tag(
                        name=tag_name.value,
                        instruction=tag_instructions.get(tag_name, f"Tag for {tag_name.value}")
                    )
                    new_tags.append(new_tag)
            
            if new_tags:
                session.add_all(new_tags)
                await session.commit()
                print(f"Created {len(new_tags)} new tags")
            else:
                print("All tags already exist")
        except Exception as e:
            await session.rollback()
            print(f"Error creating tags: {e}")
            raise
        finally:
            # Session is automatically closed by the async generator
            break

if __name__ == "__main__":
    import asyncio
    asyncio.run(create_default_tags())