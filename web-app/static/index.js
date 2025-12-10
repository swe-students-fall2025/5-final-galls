document.addEventListener("DOMContentLoaded", () => {
    const bookMarkBtns = document.querySelectorAll('.recipe-bookmark');

    bookMarkBtns.forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();

           const recipeId = btn.dataset.id;
            
            try { 
                console.log('clicked! ');
                const res = await fetch(`/recipes/${recipeId}/bookmarked`, {
                    method: 'POST'
                });

                console.log("2")
                if(res.ok) { 
                    btn.classList.toggle('active');  
                    btn.querySelector("svg path").style.fill = "rgb(223, 188, 30)";
                } else { 
                    alert("Error adding recipe to bookmarked recipes 1");
                }
            } catch (err) { 
                console.log('3')
                console.error(err);
                alert("Error adding recipe to bookmarked recipes 2")
            }
        });
    });
 });