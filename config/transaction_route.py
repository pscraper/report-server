from typing import Annotated, Callable, Any
from fastapi import Depends, Request, Response
from fastapi.routing import APIRoute
from sqlmodel import Session
from config.engine_config import EngineConfig


class TransactionRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            with Session(EngineConfig.get_engine) as session:
                try:
                    print("Start Transaction")
                    result = await original_route_handler(request)
                    session.flush()
                    session.commit()
                    print("End Transaction")
                    return result
                    
                except Exception as e:
                    session.rollback()
                    raise e
                
                finally:
                    session.close()
            
        return custom_route_handler 
        
