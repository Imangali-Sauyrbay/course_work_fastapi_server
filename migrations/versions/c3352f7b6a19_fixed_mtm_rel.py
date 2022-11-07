"""fixed mtm rel

Revision ID: c3352f7b6a19
Revises: a3afc053c284
Create Date: 2022-11-06 16:00:48.626835

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'c3352f7b6a19'
down_revision = 'a3afc053c284'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('product_seller', sa.Column('price', sa.Integer(), nullable=False))
    op.add_column('product_seller', sa.Column('currency', sa.String(length=255), nullable=True))
    op.drop_column('products', 'currency')
    op.drop_column('products', 'price')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('products', sa.Column('price', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False))
    op.add_column('products', sa.Column('currency', mysql.VARCHAR(length=255), nullable=True))
    op.drop_column('product_seller', 'currency')
    op.drop_column('product_seller', 'price')
    # ### end Alembic commands ###
