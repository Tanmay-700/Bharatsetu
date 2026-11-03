import pytest
from app.services.routing.jev_router import JevRouter

@pytest.mark.asyncio
async def test_jev_router_single_domain():
    result = await JevRouter.route(
        question="How many days of leave do I have?",
        available_domains=["HR Policies"]
    )
    assert result["domains"] == ["HR Policies"]
    assert result["confidence"] == 1.0

@pytest.mark.asyncio
async def test_jev_router_empty_domains():
    result = await JevRouter.route(
        question="What is current?",
        available_domains=[]
    )
    assert result["domains"] == []
