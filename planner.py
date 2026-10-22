import json
import threading
import uuid
from datetime import datetime
from core import execute_task

class Planner:
    def __init__(self):
        self.plans = {}
    
    def create_plan(self, tasks):
        plan_id = str(uuid.uuid4())
        self.plans[plan_id] = {
            "tasks": [{"text": t, "status": "pending", "result": None} for t in tasks],
            "current": 0,
            "created_at": datetime.now().isoformat()
        }
        thread = threading.Thread(target=self._execute_plan, args=(plan_id,))
        thread.start()
        return plan_id
    
    def get_status(self, plan_id):
        return self.plans.get(plan_id)
    
    def _execute_plan(self, plan_id):
        plan = self.plans[plan_id]
        tasks = plan["tasks"]
        
        for i, task in enumerate(tasks):
            if task["status"] != "pending":
                continue
            
            plan["current"] = i
            task["status"] = "running"
            
            try:
                reply, _ = execute_task(task["text"])
                if "Ошибка" in str(reply) or "Не удалось" in str(reply):
                    task["status"] = "error"
                else:
                    task["status"] = "success"
                task["result"] = str(reply)[:500]
            except Exception as e:
                task["status"] = "error"
                task["result"] = str(e)[:500]
        
        plan["current"] = -1

planner = Planner()