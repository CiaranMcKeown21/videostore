"""adding games

Revision ID: 1e7559641331
Revises: d6aebd83e929
Create Date: 2021-12-05 19:52:15.718520

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e7559641331'
down_revision = 'd6aebd83e929'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('game',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.Column('description', sa.String(length=250), nullable=True),
    sa.Column('release_year', sa.Integer(), nullable=True),
    sa.Column('rating', sa.Integer(), nullable=True),
    sa.Column('last_update', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('game')
    # ### end Alembic commands ###