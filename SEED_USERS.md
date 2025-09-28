# Seed Users Documentation

This document explains how to use the seed users management command to create test users for the Franklin Search application.

## Overview

The `seed_users` command creates predefined test users that can be used for development and testing purposes. This eliminates the need to manually create users every time you set up the application.

## Created Users

The command creates two users by default:

### Test User (Regular User)
- **Username**: `testuser`
- **Email**: `test@franklin.com`
- **Password**: `testpass123`
- **Role**: Regular User
- **Permissions**: Can search apps, write reviews

### Supervisor
- **Username**: `supervisor`
- **Email**: `supervisor@franklin.com`
- **Password**: `supervisor123`
- **Role**: Supervisor
- **Permissions**: Can approve/reject reviews, access admin features

## Usage

### Basic Usage
```bash
python manage.py seed_users
```

This will create both users if they don't already exist.

### Reset Existing Users
```bash
python manage.py seed_users --reset
```

This will delete existing seed users and create fresh ones with the same credentials.

### Skip Existing Users (Default Behavior)
```bash
python manage.py seed_users --skip-existing
```

This will skip creating users that already exist (this is the default behavior).

## Integration with Application Setup

### For New Installations
After setting up your Franklin Search application:

1. Run database migrations:
   ```bash
   python manage.py migrate
   ```

2. Create seed users:
   ```bash
   python manage.py seed_users
   ```

3. Start the development server:
   ```bash
   python manage.py runserver
   ```

4. Login with the provided credentials to test the application.

### For Development/Testing
When you need to test different user roles:

1. Use the test user to test regular user functionality (searching, writing reviews)
2. Use the supervisor to test admin functionality (approving reviews)

## Security Notes

⚠️ **Important**: These are test credentials and should **NEVER** be used in production environments.

For production:
- Use strong, unique passwords
- Create users through proper admin interfaces
- Consider using environment variables for sensitive data

## Customizing Seed Data

To modify the seed users, edit the `seed_users` array in:
```
accounts/management/commands/seed_users.py
```

You can change:
- Usernames and emails
- Passwords
- Names
- Roles
- Additional user attributes

## Troubleshooting

### User Already Exists Error
If you get an error that a user already exists:
- Use `--reset` to delete and recreate users
- Or delete the users manually through Django admin

### Permission Errors
If you get permission errors:
- Make sure your database is set up correctly
- Ensure you have the necessary database permissions
- Check that migrations have been applied

### Email Conflicts
If you get email conflict errors:
- Check if there are existing users with the same email addresses
- Use `--reset` to clear existing users
- Or modify the email addresses in the seed data

## Example Output

```
🌱 Starting user seeding process...
✅ Created regular_user: testuser
     Full name: Test User
     Email: test@franklin.com
     Role: Regular User
     Is supervisor: False

✅ Created supervisor: supervisor
     Full name: Admin Supervisor
     Email: supervisor@franklin.com
     Role: Supervisor
     Is supervisor: True

🎉 User seeding completed!
   Created: 2 users
   Skipped: 0 users

📝 Login Credentials:
   Test User:
     Username: testuser
     Password: testpass123
     Role: Regular User

   Supervisor:
     Username: supervisor
     Password: supervisor123
     Role: Supervisor

🚀 You can now login with these credentials!
```