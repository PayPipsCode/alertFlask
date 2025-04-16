"""Make txn_id nullable

Revision ID: a617dc4218fd
Revises: a248fd277644
Create Date: 2025-04-16 14:08:01.837855
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a617dc4218fd'
down_revision = 'a248fd277644'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('subscribers', schema=None) as batch_op:
        batch_op.alter_column('txn_id',
            existing_type=sa.String(length=50),
            nullable=True
        )

def downgrade():
    with op.batch_alter_table('subscribers', schema=None) as batch_op:
        batch_op.alter_column('txn_id',
            existing_type=sa.String(length=50),
            nullable=False
        )
