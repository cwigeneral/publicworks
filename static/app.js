const rhythmsEl=document.querySelector("#rhythms");const conditionsEl=document.querySelector("#conditions");const countEl=document.querySelector("#count");const panel=document.querySelector("#panel");let selected=null;

async function load(){
  const data=await fetch("/api/state").then(r=>r.json());
  const ordinary=data.rhythms.filter(r=>r.domain!=="Parks");
  const parks=data.rhythms.filter(r=>r.domain==="Parks");
  const parkPlaces=[...new Set(parks.map(r=>r.place))];

  const ordinaryHtml=ordinary.map(r=>rhythmButton(r)).join("");
  const parksHtml=parkPlaces.length?`<div class="domain"><div class="domain-head"><strong>PARKS</strong><span>Witness by place</span></div><div class="park-list">${parkPlaces.map(place=>{
    const items=parks.filter(r=>r.place===place);
    return `<div class="place-card"><div class="place-name">${place}</div><div class="context-grid">${items.map(r=>rhythmButton(r,true)).join("")}</div></div>`;
  }).join("")}</div></div>`:"";

  rhythmsEl.innerHTML=ordinaryHtml+parksHtml;
  countEl.textContent=data.conditions.length;
  conditionsEl.innerHTML=data.conditions.length?data.conditions.map(c=>`<div class="condition-card"><span class="mark">${c.state==="act"?"■":"△"}</span><div><strong>${c.name}</strong><p>${c.place}</p></div><span class="route">${c.route}</span></div>`).join(""):`<div class="empty">No active conditions. The rhythm continues.</div>`;
}
function rhythmButton(r,compact=false){
  const label=compact?r.context:r.name;
  const sub=compact?"":`<div class="muted">${r.place}</div>`;
  return `<button class="rhythm ${compact?"context":""}" data-id="${r.id}" data-name="${label}" data-place="${r.place}"><div class="rhythm-row"><div><strong>${label}</strong>${sub}</div><span class="status">${symbol(r.latest_condition)}</span></div></button>`;
}
function symbol(s){return s==="good"?"●":s==="watch"?"△":s==="act"?"■":"○"}
rhythmsEl.addEventListener("click",e=>{const b=e.target.closest(".rhythm");if(!b)return;selected=Number(b.dataset.id);document.querySelector("#panel-title").textContent=b.dataset.name;document.querySelector("#panel-place").textContent=b.dataset.place;panel.showModal()});
document.querySelector(".close").addEventListener("click",()=>panel.close());
document.querySelector(".condition-grid").addEventListener("click",async e=>{const b=e.target.closest("[data-condition]");if(!b||!selected)return;b.disabled=true;await fetch("/api/witness",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({rhythm_id:selected,condition:b.dataset.condition})});panel.close();b.disabled=false;await load()});
load();
