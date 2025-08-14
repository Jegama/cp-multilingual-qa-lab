"""
Multi-step reasoning chains for enhanced theological responses.

This module contains workflow functions that combine multiple AI generations
with review processes to improve answer quality and theological accuracy.
"""

from typing import Union
import parrot_ai.prompts as parrot_prompts
from .core import ParrotAI, ParrotAIHF  # lightweight (ParrotAI heavy deps are lazy)


def parrot_chain(data, parrot_instance: Union[ParrotAI, ParrotAIHF]):
    """
    Execute a multi-step reasoning chain for theological questions.
    
    This chain generates multiple candidate answers, reviews them through
    a Calvin-based theological lens, and produces a final refined answer.
    
    Args:
        data: List containing the conversation data, where data[0] is the user question
              and data[1] is the verified answer from the dataset
        parrot_instance: An initialized ParrotAI instance with a loaded model
    
    Returns:
        dict: Contains all intermediate outputs and the final answer
    """
    if not parrot_instance.is_loaded():
        raise ValueError("ParrotAI instance must have a loaded model")
    
    question = data[0]["content"]

    # Step 1: Generate the Candidate Answers
    reasoning_prompt = parrot_prompts.reasoning_prompt.format(
        user_question=question
    )

    # Verified answer from the dataset
    first_answer = data[1]["content"]

    # Second answer using the main system prompt
    second_answer = parrot_instance.generate(
        reasoning_prompt,
        system=parrot_prompts.MAIN_SYSTEM_PROMPT
    )

    # Third answer using the Calvin system prompt
    third_answer = parrot_instance.generate(
        reasoning_prompt,
        system=parrot_prompts.CALVIN_SYS_PROMPT
    )

    # Step 2: Calvin Review (depends on all three answers)
    review_prompt = parrot_prompts.calvin_review_prompt.format(
        user_question=question,
        first_answer=first_answer,
        second_answer=second_answer,
        third_answer=third_answer
    )
    calvin_review = parrot_instance.generate(
        review_prompt,
        system=parrot_prompts.CALVIN_SYS_PROMPT
    )

    # Step 3: Final Answer (depends on the review)
    final_answer_prompt = parrot_prompts.final_answer_prompt.format(
        user_question=question,
        first_answer=first_answer,
        second_answer=second_answer,
        third_answer=third_answer,
        calvin_review=calvin_review
    )

    final_answer = parrot_instance.generate(
        final_answer_prompt,
        system=parrot_prompts.MAIN_SYSTEM_PROMPT
    )

    return {
        "first_answer": first_answer,
        "second_answer": second_answer,
        "third_answer": third_answer,
        "calvin_review": calvin_review,
        "final_answer": final_answer
    }


def simple_chain(question: str, parrot_instance: Union[ParrotAI, ParrotAIHF]):
    """
    Execute a simple single-step generation for quick responses.
    
    Args:
        question: The user's question as a string
        parrot_instance: An initialized ParrotAI instance with a loaded model
    
    Returns:
        str: The generated response
    """
    if not parrot_instance.is_loaded():
        raise ValueError("ParrotAI instance must have a loaded model")
    
    reasoning_prompt = parrot_prompts.reasoning_prompt.format(
        user_question=question
    )
    
    return parrot_instance.generate(
        reasoning_prompt,
        system=parrot_prompts.MAIN_SYSTEM_PROMPT
    )


def comparative_chain(question: str, parrot_instance: Union[ParrotAI, ParrotAIHF], system_prompts: list):
    """
    Generate responses using multiple system prompts for comparison.
    
    Args:
        question: The user's question
        parrot_instance: An initialized ParrotAI instance with a loaded model
        system_prompts: List of system prompts to use for generation
    
    Returns:
        dict: Mapping of prompt names to generated responses
    """
    if not parrot_instance.is_loaded():
        raise ValueError("ParrotAI instance must have a loaded model")
    
    reasoning_prompt = parrot_prompts.reasoning_prompt.format(
        user_question=question
    )
    
    results = {}
    for i, system_prompt in enumerate(system_prompts):
        response = parrot_instance.generate(
            reasoning_prompt,
            system=system_prompt
        )
        results[f"response_{i+1}"] = response
    
    return results
