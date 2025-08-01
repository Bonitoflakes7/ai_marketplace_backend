"""added created_at in prompt

Revision ID: 190ef07cc154
Revises: 778fb3c20409
Create Date: 2025-07-31 15:47:00.204614

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '190ef07cc154'
down_revision = '778fb3c20409'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('prompt', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('prompt', schema=None) as batch_op:
        batch_op.drop_column('created_at')

    # ### end Alembic commands ###
