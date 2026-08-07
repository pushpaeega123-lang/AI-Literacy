// ======================================
// AI Learning Support Assistant
// main.js
// ======================================

// Page Loaded
document.addEventListener("DOMContentLoaded", function () {

    console.log("AI Learning Support Assistant Loaded Successfully!");

    animateCards();

    animateProgress();

    animateCounters();

    welcomeMessage();

    currentDate();

});


// ======================================
// Show / Hide Password
// ======================================

function togglePassword(id){

    let input=document.getElementById(id);

    if(input.type==="password"){

        input.type="text";

    }

    else{

        input.type="password";

    }

}


// ======================================
// Progress Bar Animation
// ======================================

function animateProgress(){

    const progressBars=document.querySelectorAll(".progress-bar");

    progressBars.forEach(function(bar){

        let value=bar.style.width;

        bar.style.width="0%";

        setTimeout(function(){

            bar.style.width=value;

        },300);

    });

}


// ======================================
// Counter Animation
// ======================================

function animateCounters(){

    const counters=document.querySelectorAll(".stat-card h2");

    counters.forEach(counter=>{

        let target=parseInt(counter.innerText);

        if(isNaN(target)) return;

        let count=0;

        let speed=25;

        let interval=setInterval(()=>{

            count++;

            counter.innerText=count;

            if(count>=target){

                counter.innerText=target;

                clearInterval(interval);

            }

        },speed);

    });

}


// ======================================
// Card Animation
// ======================================

function animateCards(){

    const cards=document.querySelectorAll(".card");

    cards.forEach((card,index)=>{

        card.style.opacity="0";

        card.style.transform="translateY(40px)";

        setTimeout(()=>{

            card.style.transition=".6s";

            card.style.opacity="1";

            card.style.transform="translateY(0)";

        },index*150);

    });

}


// ======================================
// Welcome Popup
// ======================================

function welcomeMessage(){

    let welcome=document.getElementById("welcome");

    if(welcome){

        welcome.classList.add("fade-up");

    }

}


// ======================================
// Current Date
// ======================================

function currentDate(){

    let date=document.getElementById("today");

    if(date){

        const today=new Date();

        date.innerHTML=today.toDateString();

    }

}


// ======================================
// Sidebar Active Menu
// ======================================

const navLinks=document.querySelectorAll(".sidebar .nav-link");

navLinks.forEach(link=>{

    link.addEventListener("click",function(){

        navLinks.forEach(item=>{

            item.classList.remove("active");

        });

        this.classList.add("active");

    });

});


// ======================================
// Button Click Effect
// ======================================

const buttons=document.querySelectorAll(".btn");

buttons.forEach(btn=>{

    btn.addEventListener("click",function(){

        btn.style.transform="scale(.96)";

        setTimeout(()=>{

            btn.style.transform="scale(1)";

        },120);

    });

});


// ======================================
// Floating Image
// ======================================

const images=document.querySelectorAll("img");

images.forEach(img=>{

    img.addEventListener("mouseover",()=>{

        img.style.transform="scale(1.05)";

    });

    img.addEventListener("mouseout",()=>{

        img.style.transform="scale(1)";

    });

});


// ======================================
// Scroll Animation
// ======================================

const observer=new IntersectionObserver(entries=>{

    entries.forEach(entry=>{

        if(entry.isIntersecting){

            entry.target.classList.add("fade-up");

        }

    });

});

document.querySelectorAll(".card").forEach(card=>{

    observer.observe(card);

});


// ======================================
// Back To Top Button
// ======================================

const topButton=document.createElement("button");

topButton.innerHTML="⬆";

topButton.id="topBtn";

document.body.appendChild(topButton);

topButton.style.position="fixed";
topButton.style.bottom="25px";
topButton.style.right="25px";
topButton.style.width="50px";
topButton.style.height="50px";
topButton.style.border="none";
topButton.style.borderRadius="50%";
topButton.style.background="#2563eb";
topButton.style.color="white";
topButton.style.fontSize="22px";
topButton.style.cursor="pointer";
topButton.style.display="none";
topButton.style.boxShadow="0 10px 20px rgba(0,0,0,.2)";

window.addEventListener("scroll",()=>{

    if(window.scrollY>300){

        topButton.style.display="block";

    }

    else{

        topButton.style.display="none";

    }

});

topButton.onclick=function(){

    window.scrollTo({

        top:0,

        behavior:"smooth"

    });

};


// ======================================
// Dynamic Client-side Translations & AJAX Profile Updates
// ======================================

function updateDOMTranslations(trans) {
    if (!trans) return;
    
    const mapping = {
        '.navbar-brand': 'site_title',
        'a[href="/"]': 'nav_home',
        'a[href="/dashboard"]': 'nav_dashboard',
        'a[href="/week-module"]': 'nav_learning_modules',
        'a[href="/parent-progress"]': 'nav_parent_corner',
        'a[href="/calendar-log"]': 'nav_study_log',
        'a[href="/admin"]': 'nav_admin_panel',
        'a[href="/profile"]': 'nav_profile_menu',
        'a[href="/logout"]': 'nav_logout',
        'h2.fw-bold': 'dashboard_title',
        'h3.mt-4': 'dashboard_profile_title'
    };
    
    for (const [selector, key] of Object.entries(mapping)) {
        document.querySelectorAll(selector).forEach(el => {
            if (trans[key]) {
                const icon = el.querySelector('i');
                if (icon) {
                    el.innerHTML = '';
                    el.appendChild(icon);
                    el.appendChild(document.createTextNode(' ' + trans[key]));
                } else {
                    el.innerText = trans[key];
                }
            }
        });
    }
    
    document.querySelectorAll('[data-translate]').forEach(el => {
        const key = el.getAttribute('data-translate');
        if (trans[key]) {
            el.innerText = trans[key];
        }
    });
}

document.addEventListener("DOMContentLoaded", function () {
    const profileForm = document.querySelector('form[action="/update_profile"]');
    if (profileForm) {
        profileForm.addEventListener("submit", function (e) {
            e.preventDefault();
            
            console.log("[DEBUG] Button clicked");
            
            // Validate required fields
            const formData = new FormData(profileForm);
            const fullname = (formData.get("fullname") || "").trim();
            if (!fullname) {
                console.error("[DEBUG] Form validation failed: Full Name is required.");
                alert("Please enter your full name.");
                return;
            }
            
            console.log("[DEBUG] Form validation passed");
            
            const payload = {
                fullname: fullname,
                dob: formData.get("dob"),
                gender: formData.get("gender"),
                avatar: formData.get("avatar"),
                current_mascot_dress: formData.get("current_mascot_dress"),
                preferred_language: formData.get("preferred_language"),
                learning_language: formData.get("learning_language"),
                learning_level: formData.get("learning_level")
            };
            
            console.log("[DEBUG] Request sent -> Payload:", payload);
            
            fetch('/update_profile', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(data => {
                console.log("[DEBUG] Request received -> Response:", data);
                if (data.status === 'success') {
                    if (data.translations) {
                        updateDOMTranslations(data.translations);
                    }
                    
                    // Display required success message
                    const alertDiv = document.createElement('div');
                    alertDiv.className = 'alert alert-success alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x m-3 z-3 shadow-lg rounded-4';
                    alertDiv.role = 'alert';
                    alertDiv.innerHTML = `
                        <strong>Success!</strong> Profile updated successfully.
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    `;
                    document.body.appendChild(alertDiv);
                    
                    // Update passport info in DOM immediately
                    const nameHeader = document.querySelector('.profile-passport-card h3');
                    if (nameHeader) nameHeader.innerText = data.fullname;
                    
                    // Refresh session view after brief delay so AI Tutor & Dashboard update seamlessly without logout/login
                    setTimeout(() => {
                        window.location.reload();
                    }, 800);
                } else {
                    console.error("[DEBUG] Profile Update Failed:", data.message || "Unknown error");
                    alert(data.message || "Failed to update profile.");
                }
            })
            .catch(err => {
                console.error("[DEBUG] Request failed with error:", err);
                alert("An error occurred while updating profile.");
            });
        });
    }
});

console.log("Developed using Flask + Bootstrap + JavaScript");