"""empty message

Revision ID: cf761fb6dca5
Revises: e592779a613d
Create Date: 2021-06-22 02:27:09.045679

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cf761fb6dca5'
down_revision = 'e592779a613d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'Artist', ['phone'])
    op.create_unique_constraint(None, 'Venue', ['phone'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'Venue', type_='unique')
    op.drop_constraint(None, 'Artist', type_='unique')
    # ### end Alembic commands ###