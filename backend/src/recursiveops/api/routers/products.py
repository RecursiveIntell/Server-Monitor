from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from recursiveops.api.deps import get_current_user, get_session
from recursiveops.db.models import Product

router = APIRouter(prefix="/products", tags=["products"])


@router.get("")

def list_products(session: Session = Depends(get_session), _user=Depends(get_current_user)):
    return session.exec(select(Product)).all()


@router.get("/{product_id}")

def get_product(product_id: int, session: Session = Depends(get_session), _user=Depends(get_current_user)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product
