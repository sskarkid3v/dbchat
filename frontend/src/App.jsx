import { useState } from 'react'
import axios from 'axios'

function App() {
  const [messages, setMessages] = useState([{role:'system', content:'Ask about DB'}])
  const [input, setInput] = useState('')

  const send = async () => {
    if(!input) return
    setMessages(m => [...m, {role:'user', content: input}])
    try {
      const res = await axios.post('http://localhost:8000/chat', { message: input })
      setMessages(m => [...m, {role:'assistant', content: res.data}])
    } catch(e) {
      setMessages(m => [...m, {role:'assistant', content: { error: e.message }}])
    }
    setInput('')
  }

  return (
    <div style={{maxWidth:900, margin:'16px auto'}}>
      <h3>DB Chat POC</h3>
      <div style={{height:520, overflow:'auto', border:'1px solid #ddd', padding:12}}>
        {messages.map((m,i)=>(
          <div key={i} style={{marginBottom:12}}>
            <b>{m.role}:</b>
            {typeof m.content === 'string' ? <div>{m.content}</div> :
              m.content.error ? <div style={{color:'red'}}>{m.content.error}</div> :
              <div>
                {m.content.narrative && <p>{m.content.narrative}</p>}
                {m.content.sql && <pre>{m.content.sql}</pre>}
                {m.content.columns && (
                  <table border="1" cellPadding="4">
                    <thead><tr>{m.content.columns.map(c=> <th key={c}>{c}</th>)}</tr></thead>
                    <tbody>
                      {m.content.rows.map((r,ri) => <tr key={ri}>{r.map((cell,ci)=><td key={ci}>{String(cell)}</td>)}</tr>)}
                    </tbody>
                  </table>
                )}
              </div>
            }
          </div>
        ))}
      </div>
      <div style={{display:'flex', gap:8, marginTop:8}}>
        <input style={{flex:1}} value={input} onChange={e=>setInput(e.target.value)} onKeyDown={e => e.key==='Enter' && send()} placeholder="Ask: top customers by amount" />
        <button onClick={send}>Send</button>
      </div>
    </div>
  )
}

export default App
