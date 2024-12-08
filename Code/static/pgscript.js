// 사용자의 입력을 받아서 OpenAI API를 호출하는 함수
async function fetchRecommendations(userQuery) {
    const response = await fetch('/recommend', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: userQuery }),
    });
    const data = await response.json();
    return data.programs; // 추천된 프로그램 목록 반환
}

// 검색 버튼 클릭 시 이벤트 처리
document.getElementById('search-button').addEventListener('click', async () => {
    const userInput = document.getElementById('user-input').value;
    const programList = document.getElementById('program-list');
    programList.innerHTML = '';  // 이전 결과 초기화

    if (userInput) {
        const programs = await fetchRecommendations(userInput); // 추천된 프로그램 받아오기
        programs.forEach(program => {
            const listItem = document.createElement('li');
            listItem.textContent = program;
            programList.appendChild(listItem);
        });
    } else {
        programList.innerHTML = '<li>프로그램을 입력하세요.</li>';
    }
});
function showLoader() {
    document.getElementById("loader").style.display = "flex"; // 로딩 화면 표시
}