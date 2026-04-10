def soc_triage_grader(trajectory: dict = None) -> float:
    """
    Evaluates the agent's trajectory. 
    Survives the OpenEnv Phase 2 Reflection Trap.
    """
    if trajectory is None:
        return 0.50

    try:
        steps = trajectory.get("history", [])
        if not steps:
            return 0.01

        step_count = len(steps)
        success = False

        for step in steps:
            action_data = step.get("action", {})
            action_str = str(action_data)
            
            if "block_ip" in action_str:
                success = True
                break

        if success:
            final_score = 0.99 - (step_count * 0.02)
            return max(0.01, min(0.99, round(final_score, 2)))
        else:
            return 0.10

    except Exception as e:
        return 0.01
