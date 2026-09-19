const rhythmsEl=document.querySelector("#rhythms");const conditionsEl=document.querySelector("#conditions");const countEl=document.querySelector("#count");const panel=document.querySelector("#panel");const conditionStep=document.querySelector("#condition-step");const attentionStep=document.querySelector("#attention-step");const standardStep=document.querySelector("#standard-step");const standardOpen=document.querySelector("#standard-open");let selected=null;let selectedContext=null;

async function load(){
  const data=await fetch("/api/state").then(r=>r.json());
  const ordinary=data.rhythms.filter(r=>r.domain!=="Parks");
  const parks=data.rhythms.filter(r=>r.domain==="Parks");
  const parkPlaces=[...new Set(parks.map(r=>r.place))];
  const ordinaryHtml=ordinary.map(r=>rhythmButton(r)).join("");
  const parksHtml=parkPlaces.length?`<div class="domain"><div class="domain-head"><strong>PARKS</strong><span>Witness by place</span></div><div class="park-list">${parkPlaces.map(place=>{const items=parks.filter(r=>r.place===place);return `<div class="place-card"><div class="place-name">${place}</div><div class="context-grid">${items.map(r=>rhythmButton(r,true)).join("")}</div></div>`;}).join("")}</div></div>`:"";
  rhythmsEl.innerHTML=ordinaryHtml+parksHtml;
  countEl.textContent=data.conditions.length;
  conditionsEl.innerHTML=data.conditions.length?data.conditions.map(c=>`<div class="condition-card"><span class="mark">${fieldMark(c.state)}</span><div><strong>${c.name}</strong><p>${c.attention?attentionLabel(c.attention)+" · ":""}${c.place}</p></div><span class="route">${c.route}</span></div>`).join(""):`<div class="empty">No active conditions. The rhythm continues.</div>`;
}
function rhythmButton(r,compact=false){const label=compact?r.context:r.name;const sub=compact?"":`<div class="muted">${r.place}</div>`;return `<button class="rhythm ${compact?"context":""}" data-id="${r.id}" data-name="${label}" data-place="${r.place}" data-context="${r.context}" data-domain="${r.domain}"><div class="rhythm-row"><div><strong>${label}</strong>${sub}</div><span class="status">${symbol(r.latest_condition)}</span></div></button>`;}
function fieldMark(s){return s==="good"?`<span class="field-mark mark-good small"><i></i></span>`:s==="watch"?`<span class="field-mark mark-watch small"><i></i></span>`:s==="act"?`<span class="field-mark mark-act small"><i></i></span>`:"○"}
function symbol(s){return s?fieldMark(s):"○"}
function attentionLabel(s){return {mow:"Mow",weeds:"Weeds",water:"Water",clean:"Clean",damage:"Damage",other:"Other"}[s]||s}
function resetPanel(){conditionStep.hidden=false;attentionStep.hidden=true;standardStep.hidden=true;standardOpen.hidden=!(selectedContext?.domain==="Parks"&&selectedContext?.context==="Grounds")}
async function submitWitness(condition,attention=null){await fetch("/api/witness",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({rhythm_id:selected,condition,attention})});panel.close();resetPanel();await load()}
rhythmsEl.addEventListener("click",e=>{const b=e.target.closest(".rhythm");if(!b)return;selected=Number(b.dataset.id);selectedContext={domain:b.dataset.domain,context:b.dataset.context};document.querySelector("#panel-title").textContent=b.dataset.name;document.querySelector("#panel-place").textContent=b.dataset.place;resetPanel();panel.showModal()});
document.querySelector(".close").addEventListener("click",()=>{panel.close();resetPanel()});
standardOpen.addEventListener("click",()=>{conditionStep.hidden=true;attentionStep.hidden=true;standardStep.hidden=false;standardOpen.hidden=true});
document.querySelector("#standard-back").addEventListener("click",resetPanel);
document.querySelector(".condition-grid").addEventListener("click",async e=>{const b=e.target.closest("[data-condition]");if(!b||!selected)return;const condition=b.dataset.condition;if(condition==="act"&&selectedContext?.domain==="Parks"&&selectedContext?.context==="Grounds"){conditionStep.hidden=true;attentionStep.hidden=false;return;}b.disabled=true;await submitWitness(condition);b.disabled=false});
document.querySelector("#attention-back").addEventListener("click",resetPanel);
document.querySelector(".attention-grid").addEventListener("click",async e=>{const b=e.target.closest("[data-attention]");if(!b||!selected)return;b.disabled=true;await submitWitness("act",b.dataset.attention);b.disabled=false});
load();
