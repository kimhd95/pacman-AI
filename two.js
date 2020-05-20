function solution(expression) {
    var answer = 0;
    const priority = [['+', '-', '*'], ['+', '*', '-'], ['-', '+', '*'], ['-', '*', '+'], ['*', '+', '-'], ['*', '-', '+']];
    const values = []
    const pe = parseExpression(expression);
    for (let i = 0; i < 6; i++) {
      const val = calculate(getPostfix(pe, priority[i]))
      values.push(Math.abs(val));
    }

    answer = Math.max.apply(0, values);
    console.log(values);
    return answer;
}

function parseExpression(expression) {
  const parsedExp = [];
  const numbers = expression.split(/[\+,\-,\*]/);
  const operators = [...expression].filter((e, index, array) => {
    return (e=='+' || e=='-' || e=='*');
  });

  for (let i = 0; i < operators.length; i++) {
    parsedExp.push(numbers[i]);
    parsedExp.push(operators[i]);
  }
  parsedExp.push(numbers[numbers.length - 1]);
  // console.log(parsedExp);
  return parsedExp;
}

function getPostfix(parsedExp, priority) {
  const stack = [];
  const postfix = [];

  for (let i = 0; i < parsedExp.length; i++) {
    console.log(postfix)
    let element = parsedExp[i];
    if (!(element == '+' || element == '-' || element == '*')) {  // 피연산자
      postfix.push(element);
    } else {  // 연산자
      if (stack.length == 0) {   // 2
        stack.push(element);
      } else {    //3, 4
        if (priority.indexOf(element) >= priority.indexOf(stack[stack.length - 1])) { //3
          postfix.push(stack.pop());
          stack.push(element);
        } else {
          stack.push(element);
        }
      }
    }
  }

  while (stack.length > 0) {    //5
    postfix.push(stack.pop());
  }
  console.log("postfix: ", postfix)

  return postfix;
}

function calculate(postfix, priority) {
  const pf = postfix
  const stack = [];
  // while(pf) {
  //
  // }
  for (let i = 0; i < postfix.length; i++) {
    let element = postfix[i];
    if (!(element == '+' || element == '-' || element == '*')) {  //1
      stack.push(element)
    } else {    //2
      let num1 = stack.pop();
      let num2 = stack.pop();
      let tempExp = String(num1) + element + String(num2);
      console.log(tempExp);
      stack.push(eval(tempExp));
    }
  }

  return stack[0];
}

console.log(solution("100-200*300-500+20"));
