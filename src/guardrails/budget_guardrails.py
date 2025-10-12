"""
Budget Guardrail for Customer Support AI Agent
Validates travel budgets and ensures realistic planning
"""

from agents import Agent, OpenAIChatCompletionsModel, Runner, GuardrailFunctionOutput
from ..data.models import BudgetAnalysis
from ..utils.config import Config

# Initialize configuration
config = Config()

# Budget analysis agent for validating travel budgets
budget_analysis_agent = Agent(
    name="Budget Analyzer",
    instructions="""
    You analyze travel budgets to determine if they are realistic for the destination and duration.
    Consider factors like:
    - Average hotel costs in the destination
    - Flight costs
    - Food and entertainment expenses
    - Local transportation
    
    Provide a clear analysis of whether the budget is realistic and why.
    If the budget is not realistic, suggest a more appropriate budget.
    Don't be harsh at all, lean towards it being realistic unless it's really crazy.
    If no budget was mentioned, just assume it is realistic.
    """,
    output_type=BudgetAnalysis,
    model=OpenAIChatCompletionsModel(model=config.MODEL_NAME, openai_client=config.openai_client),
)

async def budget_guardrail(ctx, agent, input_data):
    """
    Check if the user's travel budget is realistic.
    
    Args:
        ctx: Runtime context
        agent: The agent instance
        input_data: User input to analyze
    
    Returns:
        GuardrailFunctionOutput: Analysis result with tripwire status
    """
    try:
        # Create analysis prompt
        analysis_prompt = f"""
        The user is planning a trip and said: '{input_data}'
        
        Analyze if their budget is realistic for a trip to their destination 
        for the length they mentioned. Consider typical costs for:
        - Flights
        - Accommodation 
        - Food and drinks
        - Activities and entertainment
        - Local transportation
        """
        
        # Run budget analysis
        result = await Runner.run(budget_analysis_agent, analysis_prompt, context=ctx.context)
        final_output = result.final_output_as(BudgetAnalysis)

        # Provide feedback if budget is unrealistic
        if not final_output.is_realistic:
            print(f"⚠️ Budget Alert: {final_output.reasoning}")
            if final_output.suggested_budget:
                print(f"💡 Suggested budget: ${final_output.suggested_budget}")
        
        return GuardrailFunctionOutput(
            output_info=final_output,
            tripwire_triggered=not final_output.is_realistic,
        )
        
    except Exception as e:
        # Fallback: assume budget is realistic if analysis fails
        print(f"Budget analysis error: {str(e)}")
        return GuardrailFunctionOutput(
            output_info=BudgetAnalysis(
                is_realistic=True, 
                reasoning=f"Unable to analyze budget due to error: {str(e)}"
            ),
            tripwire_triggered=False
        )