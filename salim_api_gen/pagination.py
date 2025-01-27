from typing import Dict, Any, List, Callable


class PaginationHandler:
    def __init__(self):
        self.next_page_token: str = ""

    async def paginate(self, request_func: Callable, **kwargs) -> List[Dict[str, Any]]:
        all_results = []
        while True:
            response = await request_func(**kwargs, page_token=self.next_page_token)
            all_results.extend(response.get("results", []))
            self.next_page_token = response.get("next_page_token")
            if not self.next_page_token:
                break
        return all_results
