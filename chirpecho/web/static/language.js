document.querySelectorAll('.language-control input[type="checkbox"]').forEach(input=>input.addEventListener('change',()=>{
  const next=input.form.querySelector('input[name="next"]');
  if(next)next.value=next.value.split('#')[0]+location.hash;
  input.form.requestSubmit();
}));
