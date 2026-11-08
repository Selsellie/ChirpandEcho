document.querySelectorAll('.language-control input[type="checkbox"]').forEach(input=>input.addEventListener('change',()=>input.form.requestSubmit()));
