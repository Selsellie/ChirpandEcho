/* Native canvas spectra: local data, no chart libraries or image dependencies. */
(() => {
  'use strict';
  const nl=document.documentElement?.lang==='nl';
  const say=(en,nlText)=>nl?nlText:en;
  const cache = new Map();
  const views = new Set();
  const palette = [[0,20,45,53],[.3,40,101,104],[.65,125,186,154],[.9,214,239,135],[1,255,245,206]];
  const colors = Array.from({length:256}, (_, i) => {
    const t=i/255;
    let k=1; while(k<palette.length-1 && palette[k][0]<t)k++;
    const a=palette[k-1],b=palette[k],f=(t-a[0])/(b[0]-a[0]);
    return [1,2,3].map(c=>Math.round(a[c]+(b[c]-a[c])*f));
  });
  const number = (n,d=1) => nl?Number(n).toFixed(d).replace('.',','):Number(n).toFixed(d);
  function clock(data, fraction) {
    if(!data.window_start_at || data.duration_seconds===null)return null;
    const stamp=new Date(Date.parse(data.window_start_at)+fraction*data.duration_seconds*1000);
    return new Intl.DateTimeFormat(document.documentElement?.lang||'en',{
      hour:'2-digit',minute:'2-digit',second:'2-digit',fractionalSecondDigits:3,hourCycle:'h23',
      timeZone:document.documentElement?.dataset?.timezone||'Europe/Amsterdam'
    }).format(stamp);
  }
  function load(url) {
    if(!cache.has(url)) {
      const request=fetch(url,{headers:{Accept:'application/json'}}).then(r=>{
        if(!r.ok)throw new Error('Spectrogram unavailable'); return r.json();
      }).then(data=>{
        if(data.version!==1 || !Number.isInteger(data.width) || !Number.isInteger(data.height) || data.width<1 || data.width>384 || data.height<1 || data.height>160)throw new Error('Invalid spectrum');
        const decoded=atob(data.data);
        if(decoded.length!==data.width*data.height)throw new Error('Invalid matrix');
        data.values=Uint8Array.from(decoded,c=>c.charCodeAt(0));
        const image=document.createElement('canvas');image.width=data.width;image.height=data.height;
        const ctx=image.getContext('2d');const pixels=ctx.createImageData(data.width,data.height);
        for(let i=0;i<data.values.length;i++){
          const rgb=colors[data.values[i]];pixels.data.set([...rgb,255],i*4);
        }
        ctx.putImageData(pixels,0,0);data.image=image;return data;
      });
      cache.set(url,request);
      request.catch(()=>cache.delete(url));
    }
    return cache.get(url);
  }
  function draw(canvas) {
    const data=canvas.spectrum;
    if(!data || !canvas.isConnected)return;
    const box=canvas.getBoundingClientRect();if(box.width<1 || box.height<1)return;
    const scale=Math.min(window.devicePixelRatio||1,2), w=box.width,h=box.height;
    canvas.width=Math.round(w*scale);canvas.height=Math.round(h*scale);
    const ctx=canvas.getContext('2d');ctx.setTransform(scale,0,0,scale,0,0);
    const p={x:44,y:24,w:Math.max(1,w-59),h:Math.max(1,h-55)};canvas.plot=p;
    ctx.fillStyle='#142d35';ctx.fillRect(0,0,w,h);
    ctx.imageSmoothingEnabled=false;ctx.drawImage(data.image,p.x,p.y,p.w,p.h);
    ctx.font='10px ui-monospace, monospace';ctx.fillStyle='#bed0c5';
    ctx.fillText(data.frequency_max_hz===null?say('RELATIVE FREQUENCY','RELATIEVE FREQUENTIE'):say('FREQUENCY · kHz','FREQUENTIE · kHz'),p.x,14);
    for(let i=0;i<=4;i++){
      const f=i/4,y=p.y+p.h*(1-f),x=p.x+p.w*f;
      ctx.strokeStyle='rgba(224,239,222,.16)';ctx.lineWidth=1;
      ctx.beginPath();ctx.moveTo(p.x,y);ctx.lineTo(p.x+p.w,y);ctx.moveTo(x,p.y);ctx.lineTo(x,p.y+p.h);ctx.stroke();
      ctx.fillStyle='#bed0c5';ctx.textAlign='right';
      ctx.fillText(data.frequency_max_hz!==null?number((data.frequency_min_hz+(data.frequency_max_hz-data.frequency_min_hz)*f)/1000,0):Math.round(f*100)+'%',p.x-7,y+3);
      ctx.textAlign=i===0?'left':i===4?'right':'center';
      if(w>=650 || i%2===0){
        const stamp=clock(data,f);
        ctx.fillText(stamp || (data.duration_seconds!==null?number(data.duration_seconds*f)+'s':Math.round(f*100)+'%'),x,h-12);
      }
    }
    ctx.textAlign='left';
    if(data.highlight && data.duration_seconds>0){
      const start=data.highlight[0]/data.duration_seconds,end=data.highlight[1]/data.duration_seconds;
      ctx.strokeStyle='#e7f5bb';ctx.lineWidth=1.5;ctx.setLineDash([4,4]);
      ctx.strokeRect(p.x+start*p.w,p.y,Math.max(1,(end-start)*p.w),p.h);ctx.setLineDash([]);
    }
  }
  const observer=typeof ResizeObserver==='function'?new ResizeObserver(items=>items.forEach(item=>draw(item.target))):null;
  function attach(canvas,url,caption,readout){
    views.add(canvas);if(observer)observer.observe(canvas);
    const state=canvas.parentElement.querySelector('.spectrum-state');if(state)state.textContent=say('Loading spectrogram…','Spectrogram laden…');
    canvas.spectrum=null;canvas.getContext('2d').clearRect(0,0,canvas.width,canvas.height);
    if(caption)caption.textContent='';if(readout)readout.textContent=say('Loading signal…','Signaal laden…');
    canvas.dataset.spectrumSrc=url;
    load(url).then(data=>{
      if(canvas.dataset.spectrumSrc!==url)return;
      canvas.spectrum=data;if(state)state.textContent='';
      if(caption)caption.textContent=data.source==='legacy_png'?(data.duration_seconds!==null?say('Converted from PNG · time and frequency ranges restored from recording settings. Intensity remains image-derived.','Omgezet uit PNG · tijd en frequentiebereik hersteld uit de opname-instellingen. Intensiteit is uit het beeld afgeleid.'):say('Converted from a PNG · image-derived intensity. Axes show relative position; original numeric measurements are unavailable.','Omgezet uit PNG · intensiteit uit het beeld. De assen tonen relatieve posities; oorspronkelijke meetwaarden ontbreken.')):say('Computed from audio · relative spectral power. The dashed outline marks the detected call window.','Berekend uit audio · relatief spectraal vermogen. De stippellijn markeert het gedetecteerde roepvenster.');
      if(readout)readout.textContent=say('Move over the spectrogram to inspect the signal.','Beweeg over het spectrogram om het signaal te bekijken.');
      draw(canvas);
    }).catch(()=>{if(canvas.dataset.spectrumSrc===url && state)state.textContent=say('Spectrogram unavailable. Refresh to try again.','Spectrogram niet beschikbaar. Vernieuw om opnieuw te proberen.');});
    if(readout && !canvas.dataset.pointerReady){
      canvas.dataset.pointerReady='true';
      canvas.addEventListener('pointermove',event=>{
        const data=canvas.spectrum,p=canvas.plot;if(!data || !p)return;
        const r=canvas.getBoundingClientRect(),x=(event.clientX-r.left-p.x)/p.w,y=(event.clientY-r.top-p.y)/p.h;
        if(x<0||x>1||y<0||y>1)return;
        const col=Math.min(data.width-1,Math.floor(x*data.width)),row=Math.min(data.height-1,Math.floor(y*data.height));
        const value=data.values[row*data.width+col]/255;
        const stamp=clock(data,x);
        const time=stamp?stamp+' ('+number(x*data.duration_seconds,3)+' s)':data.duration_seconds===null?number(x*100,0)+say('% of recording','% van de opname'):number(x*data.duration_seconds,3)+' s';
        const frequency=data.frequency_max_hz===null?number((1-y)*100,0)+say('% of frequency span','% van het frequentiebereik'):number((data.frequency_min_hz+(1-y)*(data.frequency_max_hz-data.frequency_min_hz))/1000)+' kHz';
        const power=data.db_min===null?number(value*100,0)+say('% image intensity','% beeldintensiteit'):number(data.db_min+value*(data.db_max-data.db_min))+say(' dB relative power',' dB relatief vermogen');
        readout.textContent=time+' · '+frequency+' · '+power;
      });
    }
  }
  document.querySelectorAll('canvas[data-spectrum-src]').forEach(canvas=>attach(canvas,canvas.dataset.spectrumSrc,
    document.querySelector(canvas.dataset.caption||'#no-caption'),document.querySelector(canvas.dataset.readout||'#no-readout')));
  const modal=document.querySelector('#spectrum-dialog');
  if(modal){
    document.querySelectorAll('[data-spectrum-preview]').forEach(link=>link.addEventListener('click',event=>{
      if(typeof modal.showModal!=='function')return;
      event.preventDefault();modal.querySelector('h2').textContent=link.dataset.species+' · spectrogram';
      modal.showModal();attach(modal.querySelector('canvas'),link.dataset.spectrumPreview,modal.querySelector('.spectrum-caption'),modal.querySelector('.spectrum-readout'));
    }));
    modal.querySelector('[data-close-spectrum]').addEventListener('click',()=>modal.close());
    modal.addEventListener('click',event=>{if(event.target===modal)modal.close();});
  }
  if(!observer)window.addEventListener('resize',()=>views.forEach(draw));
})();
