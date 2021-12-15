"""attempted loan function 1

Revision ID: ae81116869f9
Revises: 8af5292db040
Create Date: 2021-12-15 16:32:51.198019

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ae81116869f9'
down_revision = '8af5292db040'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('show_requests',
    sa.Column('requester_id', sa.Integer(), nullable=True),
    sa.Column('requested_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['requested_id'], ['show.id'], ),
    sa.ForeignKeyConstraint(['requester_id'], ['user.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('show_requests')
    # ### end Alembic commands ###
