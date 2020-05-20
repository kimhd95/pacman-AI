function solution(numbers, hand) {
    var answer = '';
    let left_pos = '*';
    let right_pos = '#';

    for (let i = 0; i < numbers.length; i++) {
        let num = numbers[i];
        // console.log(left_pos, right_pos);

        // if (num % 3 == 1) {
        if (num == 1 || num == 4 || num == 7) {
            answer = answer + 'L';
            left_pos = num;
        // } else if (num % 3 == 0) {
        } else if (num == 3 || num == 6 || num == 9) {
            answer = answer + 'R';
            right_pos = num;
        } else {
            // let ld = getDistance(num, left_pos);
            // let rd = getDistance(num, right_pos);
            let closeHand = getCloseHand(num, left_pos, right_pos);
            // if (ld < rd) {
            if (closeHand == "left") {
                answer = answer + 'L';
                left_pos = num;
            // } else if (rd < ld) {
            } else if (closeHand == "right") {
                answer = answer + 'R';
                right_pos = num;
            } else {
                if (hand == "left") {
                    answer = answer + 'L';
                    left_pos = num;
                } else {
                    answer = answer + 'R';
                    right_pos = num;
                }
            }
        }
    }

    return answer;
}

function getPos(number) {
  const dict = {0: [1, 0], 7:[0,1], 8:[1,1], 9:[2,1], 4:[0,2], 5:[1,2], 6:[2,2], 1:[0,3], 2:[1,3], 3:[2,3], '*':[0,0], '#':[2,0]}
  // switch(number) {
  //     case 0:
  //         return [1, 0];
  //     case 7:
  //         return [0, 1];
  //     case 8:
  //         return [1, 1];
  //     case 9:
  //         return [2, 1];
  //     case 4:
  //         return [0, 2];
  //     case 5:
  //         return [1, 2];
  //     case 6:
  //         return [2, 2];
  //     case 1:
  //         return [0, 3];
  //     case 2:
  //         return [1, 3];
  //     case 3:
  //         return [2, 3];
  //     default:
  //         return [0, 0]
  // }
  console.log('num: ', number, 'loc: ', dict[number])
  return dict[number];
}

function getCloseHand(number, left_pos, right_pos) {
    let loc_num = getPos(number);
    let loc_left = getPos(left_pos);
    let loc_right = getPos(right_pos);

    const leftd = (loc_num[0] - loc_left[0])**2 + (loc_num[1] - loc_left[1])**2;
    const rightd = (loc_num[0] - loc_right[0])**2 + (loc_num[1] - loc_right[1])**2;

    if (leftd < rightd) {
      return "left";
    } else if (rightd < leftd) {
      return "right";
    } else {
      return "same";
    }
}

solution([7, 0, 8, 2, 8, 3, 1, 5, 7, 6, 2], "right");
