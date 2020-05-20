function solution(gems) {
    var answer = [];

    // {'Ruby': {'startIndex': 0, "lastIndex": 5}}

    const gemSet = new Set(gems);
    const gemArr = [...gemSet];
    const dict = {};
    const rangeArr = [];

    for (let i = 0; i < getArr.length; i++) {
      let gem = gemArr[i];
      let firstIndex = gemArr.indexOf(gem);
      let lastIndex = gemArr.lastIndexOf(gem);
      // dict[gem] = {'firstIndex': firstIndex, 'lastIndex': lastIndex};
      rangeArr.append([firstIndex, lastIndex]);
    }

    for (let range in rangeArr) {

    }
    return answer;
}
