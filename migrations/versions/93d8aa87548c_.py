"""empty message

Revision ID: 93d8aa87548c
Revises: e467342ee9e6
Create Date: 2020-06-02 13:07:20.297539

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '93d8aa87548c'
down_revision = 'e467342ee9e6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('public_id', sa.String(length=50), nullable=True))
    op.create_unique_constraint(None, 'users', ['public_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_column('users', 'public_id')
    # ### end Alembic commands ###
