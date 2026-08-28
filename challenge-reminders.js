const ROME_TIME_ZONE='Europe/Rome';

export const dailyChallengeReminderSlots=[
  {id:'morning',label:'mattina',startHour:6,endHour:12},
  {id:'midday',label:'metà giornata',startHour:12,endHour:18},
  {id:'evening',label:'sera',startHour:18,endHour:24}
];

export function italyChallengeReminderMoment(value=new Date()){
  const date=value instanceof Date?value:new Date(value);
  if(Number.isNaN(date.getTime()))return null;
  const parts=Object.fromEntries(new Intl.DateTimeFormat('en-GB',{timeZone:ROME_TIME_ZONE,year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',hourCycle:'h23'}).formatToParts(date).filter(part=>part.type!=='literal').map(part=>[part.type,part.value]));
  const hour=Number(parts.hour),slot=dailyChallengeReminderSlots.find(item=>hour>=item.startHour&&hour<item.endHour);
  if(!slot)return null;
  return{date:`${parts.year}-${parts.month}-${parts.day}`,slot:slot.id,label:slot.label,hour};
}

export function normalizeChallengeReminderHistory(value,currentDate){
  const source=value&&typeof value==='object'&&!Array.isArray(value)?value:{};
  const entries=Object.entries(source).filter(([date])=>date===currentDate).map(([date,slots])=>[date,[...new Set((Array.isArray(slots)?slots:[]).filter(slot=>dailyChallengeReminderSlots.some(item=>item.id===slot)))]]);
  return Object.fromEntries(entries);
}

export function shouldShowChallengeReminder({status,date,moment,seenSlots=[],completedDates=[]}){
  if(!moment||date!==moment.date||status==='completed')return false;
  if(completedDates.includes(moment.date)||seenSlots.includes(moment.slot))return false;
  return status==='not_started'||status==='active';
}
