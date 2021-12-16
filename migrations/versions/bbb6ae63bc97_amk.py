"""Amk

Revision ID: bbb6ae63bc97
Revises: 2e6bef0b4541
Create Date: 2021-11-09 14:46:06.867500

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bbb6ae63bc97'
down_revision = '2e6bef0b4541'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('movie', sa.Column('genre', sa.String(), nullable=True))
    op.add_column('season', sa.Column('date', sa.Date(), nullable=True))
    op.add_column('web_series', sa.Column('genre', sa.String(), nullable=True))
    op.add_column('web_series', sa.Column('date', sa.Date(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('web_series', 'date')
    op.drop_column('web_series', 'genre')
    op.drop_column('season', 'date')
    op.drop_column('movie', 'genre')
    # ### end Alembic commands ###
