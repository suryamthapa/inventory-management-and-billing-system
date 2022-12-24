"""Added purchase and vendors table

Revision ID: 767daf125c93
Revises: 9dc59a6a268b
Create Date: 2022-12-24 21:32:31.982768

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '767daf125c93'
down_revision = '9dc59a6a268b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('vendors',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('vat_number', sa.Integer(), nullable=False),
    sa.Column('vendor_name', sa.String(), nullable=False),
    sa.Column('address', sa.String(), nullable=False),
    sa.Column('phone_number', sa.String(), nullable=True),
    sa.Column('telephone', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('extra_info', sa.JSON(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('phone_number'),
    sa.UniqueConstraint('telephone'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('vendor_name')
    )
    op.create_table('purchases',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('invoice_number', sa.String(), nullable=False),
    sa.Column('date_of_purchase', sa.DateTime(), nullable=True),
    sa.Column('product_qty', sa.JSON(), nullable=False),
    sa.Column('vendor_id', sa.Integer(), nullable=False),
    sa.Column('excise_duty', sa.Integer(), nullable=True),
    sa.Column('cash_discount', sa.Integer(), nullable=True),
    sa.Column('p_discount', sa.Integer(), nullable=True),
    sa.Column('extra_discount', sa.Integer(), nullable=True),
    sa.Column('vat', sa.Integer(), nullable=True),
    sa.Column('cash_payment', sa.Integer(), nullable=True),
    sa.Column('balance_amount', sa.Integer(), nullable=True),
    sa.Column('extra_info', sa.JSON(), nullable=True),
    sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('invoice_number')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('purchases')
    op.drop_table('vendors')
    # ### end Alembic commands ###
