"""empty message

Revision ID: 1a4ce8463b04
Revises: 843794e7734b
Create Date: 2021-12-21 17:22:01.931416

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1a4ce8463b04'
down_revision = '843794e7734b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('web_series', sa.Column('trending', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('web_series', 'trending')
    # ### end Alembic commands ###
