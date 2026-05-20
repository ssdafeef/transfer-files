#include <stdio.h>
#include <string.h>
#include <ctype.h>

char stack[100];
int top = -1;

void push(char x)
{
    stack[++top] = x;
}

char pop()
{
    return stack[top--];
}

int precedence(char x)
{
    if (x == '+' || x == '-')
        return 1;
    if (x == '*' || x == '/')
        return 2;
    if (x == '^')
        return 3;
    return 0;
}

void reverse(char exp[])
{
    int i, j;
    char temp;

    for(i = 0, j = strlen(exp)-1; i < j; i++, j--)
    {
        temp = exp[i];
        exp[i] = exp[j];
        exp[j] = temp;
    }
}

void infixToPostfix(char infix[], char postfix[])
{
    int i, j = 0;
    char x;

    top = -1;

    for(i = 0; infix[i] != '\0'; i++)
    {
        char ch = infix[i];

        if(isalnum(ch))
        {
            postfix[j++] = ch;
        }

        else if(ch == '(')
        {
            push(ch);
        }

        else if(ch == ')')
        {
            while((x = pop()) != '(')
            {
                postfix[j++] = x;
            }
        }

        else
        {
            while(top != -1 && precedence(stack[top]) >= precedence(ch))
            {
                postfix[j++] = pop();
            }

            push(ch);
        }
    }

    while(top != -1)
    {
        postfix[j++] = pop();
    }

    postfix[j] = '\0';
}

void infixToPrefix(char infix[], char prefix[])
{
    char rev[100], postfix[100];
    int i;

    strcpy(rev, infix);

    reverse(rev);

    for(i = 0; rev[i] != '\0'; i++)
    {
        if(rev[i] == '(')
            rev[i] = ')';

        else if(rev[i] == ')')
            rev[i] = '(';
    }

    infixToPostfix(rev, postfix);

    reverse(postfix);

    strcpy(prefix, postfix);
}

int main()
{
    char infix[100], postfix[100], prefix[100];

    printf("Enter Infix Expression : ");
    scanf("%s", infix);

    infixToPostfix(infix, postfix);
    infixToPrefix(infix, prefix);

    printf("\nPostfix Expression : %s", postfix);
    printf("\nPrefix Expression  : %s", prefix);

    return 0;
}