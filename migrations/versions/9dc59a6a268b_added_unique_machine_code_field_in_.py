"""Added unique machine code field in about app model

Revision ID: 9dc59a6a268b
Revises: caa8dad08b60
Create Date: 2022-11-20 16:32:24.085683

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9dc59a6a268b'
down_revision = 'caa8dad08b60'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('about_app', sa.Column('unique_machine_code', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('about_app', 'unique_machine_code')
    # ### end Alembic commands ###
