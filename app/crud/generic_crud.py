from typing import List
from sqlalchemy import and_, select, update
from sqlalchemy.orm.session import Session

class GenericCrud:
    
    @classmethod
    def get_rows(cls, table_model, query_conditions: List, db_session: Session, columns: List = ['*'], offset: int = None, limit: int = None, order_by: List = None):
        rows = []
        
        try:
            query = select(*columns).select_from(table_model).where(and_(*query_conditions))
            
            if order_by and type(order_by) is list:
                query = query.order_by(*order_by)
            
            if type(offset) is int:
                query = query.offset(offset)
            
            if type(limit) is int: 
                query = query.limit(limit)
            
            rows = db_session.execute(query).all()
            
        except Exception as e:
            raise e
        
        return rows
    
    @classmethod
    def create_row(cls, table_row_data, db_session: Session, auto_commit = False):
        row = None
        try:
            row = db_session.add(table_row_data)
            
            if auto_commit:
                db_session.commit()
            
        except Exception as e:
            db_session.rollback()
            raise e
        
        return row
        
    @classmethod
    def create_multiple_rows(cls, table_rows_data: List, db_session: Session, auto_commit = False):
        try:
            db_session.add_all(table_rows_data)
            
            if auto_commit:
                db_session.commit()
            
        except Exception as e:
            db_session.rollback()
            raise e
        
    @classmethod
    def update_row(cls, table_model, query_condition: List, update_data: dict, db_session: Session, auto_commit = False):
        try:
            update_query = update(table=table_model).where(and_(*query_condition))
            
            if type(update_data) is dict:
                update_query = update_query.values(**update_data)
                db_session.execute(update_query)
            
            if auto_commit:
                db_session.commit()
            
        except Exception as e:
            db_session.rollback()
            raise e
        
    @classmethod
    def delete_row(cls, table_model, query_condition: List, db_session: Session, auto_commit = False):
        delete_response = False
        
        try:
            if len(query_condition) > 0:
                row_select_query = select(table_model).where(*query_condition)
                row = db_session.execute(row_select_query).one_or_none()
                
                if row:
                    db_session.delete(row[0])
                    delete_response = True
                    
                    if auto_commit:
                        db_session.commit()
                        
            
        except Exception as e:
            db_session.rollback()
            raise e
        
        return delete_response
    