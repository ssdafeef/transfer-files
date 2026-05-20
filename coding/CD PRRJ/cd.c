#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define MAX 100

char stack[MAX];
int top = -1;

void push(char x) {
    stack[++top] = x;
}

char pop() {
    return stack[top--];
}

int priority(char x) {
    if (x == '(') return 0;
    if (x == '+' || x == '-') return 1;
    if (x == '*' || x == '/') return 2;
    return 0;
}

struct Node {
    char data;
    struct Node* left;
    struct Node* right;
};

struct Node* newNode(char x) {
    struct Node* node = (struct Node*)malloc(sizeof(struct Node));
    node->data = x;
    node->left = node->right = NULL;
    return node;
}

// --------used it convert Infix → Postfix --------
void infixToPostfix(char infix[], char postfix[]) {
    int i, k = 0;
    char x;
    top = -1;

    for (i = 0; infix[i]; i++) {
        if (isalnum(infix[i])) {
            postfix[k++] = infix[i];
        }
        else if (infix[i] == '(') {
            push(infix[i]);
        }
        else if (infix[i] == ')') {
            while ((x = pop()) != '(')
                postfix[k++] = x;
        }
        else {
            while (top != -1 && priority(stack[top]) >= priority(infix[i]))
                postfix[k++] = pop();
            push(infix[i]);
        }
    }

    while (top != -1)
        postfix[k++] = pop();

    postfix[k] = '\0';
}

// -------- Reverse string --------
void reverse(char str[]) {
    int i, j;
    char temp;
    for (i = 0, j = strlen(str) - 1; i < j; i++, j--) {
        temp = str[i];
        str[i] = str[j];
        str[j] = temp;
    }
}

// -------- Infix → Prefix --------
void infixToPrefix(char infix[], char prefix[]) {
    char temp[MAX], postfix[MAX];
    strcpy(temp, infix);

    reverse(temp);

    for (int i = 0; temp[i]; i++) {
        if (temp[i] == '(') temp[i] = ')';
        else if (temp[i] == ')') temp[i] = '(';
    }

    infixToPostfix(temp, postfix);
    reverse(postfix);
    strcpy(prefix, postfix);
}

// -------- Build Syntax Tree --------
struct Node* buildTree(char postfix[]) {
    struct Node* stack[MAX];
    int top = -1;

    for (int i = 0; postfix[i]; i++) {
        if (isalnum(postfix[i])) {
            stack[++top] = newNode(postfix[i]);
        }
        else {
            struct Node* t = newNode(postfix[i]);
            t->right = stack[top--];
            t->left = stack[top--];
            stack[++top] = t;
        }
    }
    return stack[top];
}

// -------- Print Tree --------
void printTree(struct Node* root, int space) {
    if (root == NULL) return;

    space += 5;

    printTree(root->right, space);

    printf("\n");
    for (int i = 5; i < space; i++)
        printf(" ");
    printf("%c\n", root->data);

    printTree(root->left, space);
}

// -------- Main --------
int main() {
    char infix[MAX], postfix[MAX], prefix[MAX];

    printf("Enter Infix Expression: ");
    scanf("%s", infix);

    // Convert
    infixToPostfix(infix, postfix);
    infixToPrefix(infix, prefix);

    // Build tree
    struct Node* root = buildTree(postfix);

    // Output
    printf("\nInfix   : %s", infix);
    printf("\nPostfix : %s", postfix);
    printf("\nPrefix  : %s\n", prefix);

    printf("\nSyntax Tree:\n");
    printTree(root, 0);

    return 0;
}