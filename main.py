from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi import status
from datetime import datetime, time, timedelta, date
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

agendamentos = []
estoque = []
contas = []
usuarios = {}
loginUsuario = None
horarioInicial = datetime.strptime("09:00", "%H:%M").time()
horarioFinal = datetime.strptime("22:00", "%H:%M").time()
intervaloHoras = 1

def verificarLogin(request: Request):
    global loginUsuario
    if loginUsuario is None:
        raise HTTPException(status_code=303, detail="Redirecionando para login", headers={"Location": "/login"})

def obterHorariosDisponiveis(data: str):
    dataSelecionada = datetime.strptime(data, "%Y-%m-%d").date()
    horaAtual = datetime.combine(dataSelecionada, horarioInicial)
    horariosDisponiveis = []
    hoje = datetime.now().date()
    horaAtualAgora = datetime.now().time()

    while horaAtual.time() <= horarioFinal:
        ocupado = any(
            agendamento["data"] == data and agendamento["hora"] == horaAtual.strftime("%H:%M")
            for agendamento in agendamentos
        )
        
        if not ocupado and (dataSelecionada != hoje or horaAtual.time() > horaAtualAgora):
            horariosDisponiveis.append(horaAtual.strftime("%H:%M"))

        horaAtual += timedelta(hours=intervaloHoras)

    return horariosDisponiveis

@app.get("/", response_class=HTMLResponse, dependencies=[Depends(verificarLogin)])
async def index(request: Request):
    hoje = datetime.now().date()
    agendamentosDia = [
        ag for ag in agendamentos
        if datetime.strptime(ag["data"], "%Y-%m-%d").date() == hoje
    ]
    estoqueCritico = [prod for prod in estoque if int(prod["quantidade"]) < 5]
    contasVencer = [conta for conta in contas if conta["status"] in ["Ativa", "Atraso"]]
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "agendamentosDia": agendamentosDia,
        "estoqueCritico": estoqueCritico,
        "contasVencer": contasVencer
    })

@app.get("/login", response_class=HTMLResponse)
async def loginPagina(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def realizarLogin(request: Request, usuario: str = Form(...), senha: str = Form(...)):
    global loginUsuario
    if usuario in usuarios and usuarios[usuario]["senha"] == senha:
        loginUsuario = usuario
        return templates.TemplateResponse("index.html", {"request": request, "usuario": loginUsuario})
    return templates.TemplateResponse("login.html", {"request": request, "error": "Usuário ou senha inválidos."})

@app.get("/cadastro", response_class=HTMLResponse)
async def cadastroPagina(request: Request):
    return templates.TemplateResponse("cadastro.html", {"request": request})

@app.post("/cadastro")
async def realizarCadastro(request: Request, nome: str = Form(...), email: str = Form(...), usuario: str = Form(...), senha: str = Form(...)):
    usuarios[usuario] = {"nome": nome, "email": email, "usuario": usuario, "senha": senha}
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/logout", dependencies=[Depends(verificarLogin)])
async def logout():
    global loginUsuario
    loginUsuario = None
    return RedirectResponse("/login", status_code=303)

@app.get("/agendar", response_class=HTMLResponse, dependencies=[Depends(verificarLogin)])
async def agendar(request: Request, data: str = None):
    data = data or datetime.now().strftime("%Y-%m-%d")
    horariosDisponiveis = obterHorariosDisponiveis(data)
    hoje = date.today().isoformat()
    return templates.TemplateResponse("agendar.html", {
        "request": request,
        "data": data,
        "horariosDisponiveis": horariosDisponiveis,
        "hoje": hoje
    })

@app.post("/agendar", response_class=HTMLResponse, dependencies=[Depends(verificarLogin)])
async def realizarAgendamento(request: Request, servico: str = Form(...), data: str = Form(...), hora: str = Form(...)):
    for agendamento in agendamentos:
        if agendamento["data"] == data and agendamento["hora"] == hora:
            return templates.TemplateResponse("agendar.html", {
                "request": request,
                "data": data,
                "horariosDisponiveis": obterHorariosDisponiveis(data),
                "hoje": date.today().isoformat(),
                "mensagem": "Horário indisponível para a data selecionada."})
    nomeCliente = usuarios[loginUsuario]["nome"]
    novoAgendamento = {
        "cliente": nomeCliente,
        "servico": servico,
        "data": data,
        "hora": hora,
        "situacao": "Ativo"
    }
    agendamentos.append(novoAgendamento)
    return RedirectResponse(url="/agendamentos", status_code=303)

@app.get("/agendamentos", response_class=HTMLResponse, dependencies=[Depends(verificarLogin)])
async def listarAgendamento(request: Request):
    return templates.TemplateResponse("agendamentos.html", {
        "request": request,
        "agendamentos": agendamentos})

@app.get("/excluir_agendamento/{index}", response_class=HTMLResponse, dependencies=[Depends(verificarLogin)])
async def excluirAgendamento(index: int, request: Request):
    try:
        agendamentos.pop(index)
        mensagem = "Agendamento excluído com sucesso."
    except IndexError:
        mensagem = "Agendamento não encontrado."

    return templates.TemplateResponse("agendamentos.html", {
        "request": request,
        "agendamentos": agendamentos,
        "error": mensagem
    })

@app.get("/alterar_agendamento", response_class=HTMLResponse, dependencies=[Depends(verificarLogin)])
async def alterarAgendamento(request: Request):
    return templates.TemplateResponse("alterarAgendamento.html", {
        "request": request
    })

@app.get("/estoque", response_class=HTMLResponse, dependencies=[Depends(verificarLogin)])
async def listarEstoque(request: Request):
    return templates.TemplateResponse("estoque.html", {
        "request": request,
        "estoque": estoque})

@app.post("/estoque", response_class=HTMLResponse, dependencies=[Depends(verificarLogin)])
async def cadastrarEstoque(request: Request, nome: str = Form(...), quantidade: str = Form(...), validade: str = Form(...)):
    try:
        quantidade_int = int(quantidade)
    except ValueError:
        quantidade_int = 0
    estoque.append({"nome": nome, "quantidade": quantidade_int, "validade": validade})
    return templates.TemplateResponse("estoque.html", {
        "request": request,
        "estoque": estoque})

@app.get("/alterar_estoque", response_class=HTMLResponse, dependencies=[Depends(verificarLogin)])
async def alterarEstoque(request: Request):
    return templates.TemplateResponse("alterarEstoque.html", {
        "request": request
    })

@app.get("/excluir_produto/{index}", response_class=HTMLResponse, dependencies=[Depends(verificarLogin)])
async def excluirProduto(index: int, request: Request):
    try:
        estoque.pop(index)
        mensagem = "Produto excluído com sucesso."
    except IndexError:
        mensagem = "Produto não encontrado."

    return templates.TemplateResponse("estoque.html", {
        "request": request,
        "estoque": estoque,
        "error": mensagem
    })

@app.get("/contas", response_class=HTMLResponse, dependencies=[Depends(verificarLogin)])
async def contasPagina(request: Request):
    return templates.TemplateResponse("contas.html", {
        "request": request,
        "contas": contas})

@app.post("/contas", response_class=HTMLResponse, dependencies=[Depends(verificarLogin)])
async def cadastrarConta(request: Request, descricao: str = Form(...), valor: str = Form(...), vencimento: str = Form(...)):
    status = "Ativa"
    contas.append({"descricao": descricao, "valor": valor, "vencimento": vencimento, "status": status})
    return templates.TemplateResponse("contas.html", {
        "request": request,
        "contas": contas})

@app.get("/alterar_conta", response_class=HTMLResponse, dependencies=[Depends(verificarLogin)])
async def alterarContas(request: Request):
    return templates.TemplateResponse("alterarContas.html", {
        "request": request
    })

@app.get("/excluir_conta/{index}", response_class=HTMLResponse, dependencies=[Depends(verificarLogin)])
async def excluirConta(index: int, request: Request):
    try:
        contas.pop(index)
        mensagem = "Conta excluída com sucesso."
    except IndexError:
        mensagem = "Conta não encontrada."

    return templates.TemplateResponse("contas.html", {
        "request": request,
        "contas": contas,
        "error": mensagem
    })

@app.get("/alterar_status_conta/{index}/{status}", response_class=HTMLResponse, dependencies=[Depends(verificarLogin)])
async def alterarStatusConta(index: int, status: str, request: Request):
    try:
        if status in ["Atraso", "Paga"]:
            contas[index]["status"] = status
            mensagem = f"Status da conta alterado para {status}."
        else:
            mensagem = "Status inválido."
    except IndexError:
        mensagem = "Conta não encontrada."

    return templates.TemplateResponse("contas.html", {
        "request": request,
        "contas": contas,
        "mensagem": mensagem
    }) 

@app.get("/perfil", response_class=HTMLResponse, dependencies=[Depends(verificarLogin)])
async def perfilPagina(request: Request):
    agendamentosUsuarios = [
        agendamento for agendamento in agendamentos
        if agendamento["cliente"] == usuarios[loginUsuario]["usuario"]
    ]
    return templates.TemplateResponse("perfil.html", {
        "request": request,
        "usuario": loginUsuario,
        "agendamentos": agendamentosUsuarios})


@app.get("/relatorio/excel", response_class=FileResponse, dependencies=[Depends(verificarLogin)])
async def gerarRelatorioExcel():
    caminhoArquivo = "relatorio.xlsx"
    wb = Workbook()
    wbAgendamentos = wb.active
    wbAgendamentos.title = "Agendamentos"
    wbAgendamentos.append(["Cliente", "Serviço", "Data", "Hora", "Situação"])
    for agendamento in agendamentos:
        wbAgendamentos.append([
            agendamento["cliente"],
            agendamento["servico"],
            agendamento["data"],
            agendamento["hora"],
            agendamento["situacao"]
        ])
    
    wbEstoque = wb.create_sheet(title="Estoque")
    wbEstoque.append(["Nome", "Quantidade", "Validade"])
    for produto in estoque:
        wbEstoque.append([
            produto["nome"],
            produto["quantidade"],
            produto["validade"]
        ])

    wbContas = wb.create_sheet(title="Contas")
    wbContas.append(["Descrição", "Valor", "Vencimento", "Status"])
    for conta in contas:
        wbContas.append([
            conta["descricao"],
            conta["valor"],
            conta["vencimento"],
            conta["status"]
        ])

    wb.save(caminhoArquivo)

    return FileResponse(caminhoArquivo, media_type="applicatin/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        filename="Relatorio.xlsx")

@app.get("/relatorio/pdf", response_class=FileResponse, dependencies=[Depends(verificarLogin)])
async def gerarRelatorioPDF():
    caminhoArquivo = "relatorio.pdf"
    c = canvas.Canvas(caminhoArquivo, pagesize=letter)
    largura, altura = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, altura - 50, "Relatório de Agendamentos, Estoque e Contas")
    c.setFont("Helvetica", 12)

    c.drawString(50, altura - 100, "Agendamentos")
    y = altura - 120
    for agendamento in agendamentos:
        c.drawString(50, y, f"{agendamento['cliente']} - {agendamento['servico']} - {agendamento['data']}  {agendamento['hora']} - {agendamento['situacao']}")
        y -= 20

    c.drawString(50, y - 20, "Estoque")
    y -= 40
    for produto in estoque:
        c.drawString(50, y, f"{produto['nome']} - {produto['quantidade']} - Validade: {produto['validade']}")

    c.drawString(50, y - 20, "Contas")
    y -= 40
    for conta in contas:
        c.drawString(50, y, f"{conta['descricao']} - R${conta['valor']} - Vencimento: {conta['vencimento']} - {conta['status']}")
        y -= 20

    c.save()
    return FileResponse(caminhoArquivo, media_type="application/pdf",
                        filename="Relatorio.pdf")