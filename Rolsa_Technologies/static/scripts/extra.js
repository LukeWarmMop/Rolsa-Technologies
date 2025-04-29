document.addEventListener("DOMContentLoaded", ShowContent());

document.getElementById('button1').addEventListener('click', function() {
	var btn1options = document.getElementById('option1-buttons');
	if (btn1options.style.display === 'none' || btn1options.style.display === '')
{
		HideAllBtns()
		btn1options.style.display = 'flex';
	} else {
		btn1options.style.display = 'none';
	}
})
	
document.getElementById('button2').addEventListener('click', function() {
	var btn2options = document.getElementById('option2-buttons');
	if (btn2options.style.display === 'none' || btn2options.style.display === '')
{
		HideAllBtns()
		btn2options.style.display = 'flex';
	} else {
		btn2options.style.display = 'none';
	}
})

function HideAllBtns() {
	document.getElementById('option1-buttons').style.display = 'none';
	document.getElementById('option2-buttons').style.display = 'none';
}


function ShowContent() {
    let Buttons = document.querySelectorAll(".selectSection .button");

    for (let button of Buttons) {
        button.addEventListener('click', (e) => {

            const clickedButton = e.target;

            const active = document.querySelector(".active");

            if (active) {
                active.classList.remove("active");
            }

            clickedButton.classList.add("active");

            let allContent = document.querySelectorAll(".content");

            for (let content of allContent) {

                if (content.getAttribute('data-number') === button.getAttribute('data-number')) {
                    content.style.display = "block";
                } else {
                    content.style.display = "none";
                }
            }
        });
    }
}



	