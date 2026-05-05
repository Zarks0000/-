ALTER TABLE user_templates
    DROP COLUMN IF EXISTS image,
    DROP COLUMN IF EXISTS style,
    DROP COLUMN IF EXISTS apply_args;
