const rhythmsEl=document.querySelector("#rhythms");const conditionsEl=document.querySelector("#conditions");const countEl=document.querySelector("#count");const panel=document.querySelector("#panel");let selected=null;

async function load(){
  const data=await fetch("/api/state").then(r=>r.json());
  rhythmsEl.innerHTML=data.rhythms.map(r=>`<button class="rhythm" data-id="${r.id}" data-name="${r.name}" data-place="${r.place}"><div class="rhythm-row"><div><strong>${r.name}</strong><div class="muted">${r.place}</div></div><span class="status">${symbol(r.latest_condition)}</span></div></button>`).join("");
  countEl.textContent=data.conditions.length;
  conditionsEl.innerHTML=data.conditions.length?data.conditions.map(c=>`<div class="condition-card"><span class="mark">${c.state==="act"?"■":"△"}</span><div><strong>${c.name}</strong><p>${c.place}</p></div><span class="route">${c.route}</span></div>`).join(""):`<div class="empty">No active conditions. The rhythm continues.</div>`;
}
function symbol(s){return s==="good"?"●":s==="watch"?"△":s==="act"?"■":"○"}
rhythmsEl.addEventListener("click",e=>{const b=e.target.closest(".rhythm");if(!b)return;selected=Number(b.dataset.id);document.querySelector("#panel-title").textContent=b.dataset.name;document.querySelector("#panel-place").textContent=b.dataset.place;panel.showModal()});
document.querySelector(".close").addEventListener("click",()=>panel.close());
document.querySelector(".condition-grid").addEventListener("click",async e=>{const b=e.target.closest("[data-condition]");if(!b||!selected)return;b.disabled=true;await fetch("/api/witness",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({rhythm_id:selected,condition:b.dataset.condition})});panel.close();b.disabled=false;await load()});
load();
