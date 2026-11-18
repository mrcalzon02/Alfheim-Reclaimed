// Execute recipe callbacks only. Minecraft gameplay callbacks are never executed.
const fs = require('fs');
const vm = require('vm');
const path = require('path');
const records = [], removals = [], errors = [];
let source, serial = 0;
function ingredient(x) {
  if (typeof x !== 'string') return x;
  return x.startsWith('#') ? {tag:x.slice(1)} : {item:x};
}
function stack(x) {
  if (typeof x !== 'string') return x;
  const m = x.match(/^(\d+)x?\s+(.+)$/);
  return m ? {item:m[2],count:+m[1]} : {item:x};
}
function add(data) {
  const r = {id:`kubejs:generated/recipe_tree_${++serial}`,data,source};
  records.push(r);
  const chain = {id(id) {r.id=id;return chain;},xp(n) {data.experience=n;return chain;},
    cookingTime(n) {data.cookingtime=n;return chain;}};
  return chain;
}
const event = {
  custom:add,
  remove(filter) {removals.push({filter,source});},
  shaped(out,pattern,key) {return add({type:'minecraft:crafting_shaped',result:stack(out),pattern,key:Object.fromEntries(Object.entries(key).map(([k,v])=>[k,ingredient(v)]))});},
  shapeless(out,inputs) {return add({type:'minecraft:crafting_shapeless',result:stack(out),ingredients:inputs.map(ingredient)});},
  smelting(out,input) {return add({type:'minecraft:smelting',result:stack(out),ingredient:ingredient(input)});},
  blasting(out,input) {return add({type:'minecraft:blasting',result:stack(out),ingredient:ingredient(input)});}
};
const noop = new Proxy(()=>{}, {get:()=>noop,apply:()=>undefined});
for (const file of fs.readdirSync('kubejs/server_scripts').filter(x=>x.endsWith('.js')).sort()) {
  source = 'kubejs/server_scripts/'+file;
  const text = fs.readFileSync(source,'utf8');
  if (!text.includes('ServerEvents.recipes')) continue;
  try {
    vm.runInNewContext(text,{
      ServerEvents:{recipes(fn) {fn(event);}}, Item:{of:(item,count=1)=>({item,count})},
      console:noop,PlayerEvents:noop,BlockEvents:noop,EntityEvents:noop,LevelEvents:noop,
      LootJS:noop,Java:noop,Utils:noop
    }, {filename:source,timeout:10000});
  } catch(e) {errors.push({source,error:String(e)});}
}
fs.mkdirSync('build/recipe-tree',{recursive:true});
fs.writeFileSync('build/recipe-tree/script_recipes.json',JSON.stringify({records,removals,errors},null,2));
console.log(JSON.stringify({recipes:records.length,removals:removals.length,errors}));
if(errors.length) process.exitCode=1;
