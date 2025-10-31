import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.models import User
from faker import Faker

# Importando todos os seus models
from patrimonio.models import (
    Chave, ControleChaves, Colaborador, EsquecimentoCRACHA,
    Fornecedor, EntradaFornecedor, FornecedorServico, Entrega, Visitante,
    TrabalhadorCLT, PessoaJuridica, MEI, Autonomo, Associado,
    Integracao, QuestionarioIntegracao, IntegracaoToken,
    Ocorrencia, UserProfile, ActivityLog
)
# Importando as escolhas de base que você definiu
from patrimonio.forms._choices import BASE_CHOICES


class Command(BaseCommand):
    help = 'Preenche o banco de dados com dados fictícios usando a biblioteca Faker.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Limpa todos os dados mockados antes de criar novos.',
        )

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Iniciando o preenchimento com dados mock...'))
        fake = Faker('pt_BR')  # Usando Faker para Português-Brasil

        if kwargs['clear']:
            self.clear_data()

        try:
            # Usamos uma transação para garantir que tudo seja criado ou nada
            with transaction.atomic():
                self.create_data(fake)
            self.stdout.write(self.style.SUCCESS('Preenchimento concluído com sucesso!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ocorreu um erro: {e}'))
            self.stdout.write(self.style.ERROR('O banco de dados foi revertido ao estado anterior.'))


    def clear_data(self):
        """Limpa os dados na ordem inversa das dependências."""
        self.stdout.write(self.style.WARNING('Limpando dados antigos...'))
        
        # Ordem de deleção (do mais dependente para o menos dependente)
        ActivityLog.objects.all().delete()
        Ocorrencia.objects.all().delete()
        EsquecimentoCRACHA.objects.all().delete()
        ControleChaves.objects.all().delete()
        EntradaFornecedor.objects.all().delete()
        QuestionarioIntegracao.objects.all().delete()
        IntegracaoToken.objects.all().delete()
        Integracao.objects.all().delete()
        
        # Sub-fornecedores
        Visitante.objects.all().delete()
        FornecedorServico.objects.all().delete()
        TrabalhadorCLT.objects.all().delete()
        PessoaJuridica.objects.all().delete()
        MEI.objects.all().delete()
        Autonomo.objects.all().delete()
        Associado.objects.all().delete()
        Entrega.objects.all().delete()

        # Pais
        Fornecedor.objects.all().delete()
        Chave.objects.all().delete()
        Colaborador.objects.all().delete()
        
        # Usuários (mantém superusuários)
        User.objects.filter(is_superuser=False).delete()


    def create_data(self, fake):
        """Cria os dados mockados."""
        
        base_list = [choice[0] for choice in BASE_CHOICES]
        
        # --- 1. Usuários (para logins e chaves estrangeiras) ---
        self.stdout.write('Criando Usuários...')
        users = []
        for i in range(5):
            try:
                username = f'user{i}'
                user = User.objects.create_user(
                    username=username,
                    email=fake.email(),
                    password='123', # Senha padrão para todos
                    first_name=fake.first_name(),
                    last_name=fake.last_name()
                )
                user.profile.is_admin = (i == 0) # Tornar o primeiro usuário admin
                user.profile.is_blocked = (i == 4) # Tornar o último usuário bloqueado
                user.profile.save()
                users.append(user)
            except Exception:
                # Caso o usuário já exista, apenas o busca
                users.append(User.objects.get(username=username))

        # --- 2. Colaboradores (para crachás e chaves) ---
        self.stdout.write('Criando Colaboradores...')
        colaboradores = []
        for _ in range(20):
            colab = Colaborador.objects.create(
                matricula=fake.unique.random_number(digits=6, fix_len=True),
                nome=fake.name(),
                departamento=random.choice(['TI', 'Financeiro', 'RH', 'Operações', 'Logística', 'Manutenção'])
            )
            colaboradores.append(colab)

        # --- 3. Chaves (para ControleChaves) ---
        self.stdout.write('Criando Chaves...')
        chaves = []
        for nome_chave in ['Sala Servidor', 'Depósito TI', 'Escritório Principal', 'Portaria', 'Sala Reuniões', 'Almoxarifado']:
            chave, _ = Chave.objects.get_or_create(nome=nome_chave)
            chaves.append(chave)

        # --- 4. Fornecedores (Visitantes e Prestadores) ---
        self.stdout.write('Criando Fornecedores, Visitantes e Prestadores...')
        fornecedores_list = []
        subcategorias_fornecedor = [s[0] for s in Fornecedor.SUBCATEGORIAS]

        # Criar 10 Visitantes
        for _ in range(10):
            f = Fornecedor.objects.create(
                categoria='VISITANTE',
                status=random.choice(['Sem integração', 'Integrado', 'Pendente'])
            )
            Visitante.objects.create(
                fornecedor=f,
                nome=fake.name(),
                documento=fake.cpf(),
                motivo_visita=fake.sentence(nb_words=4)
                # foto_visitante é ImageField, deixamos em branco
            )
            fornecedores_list.append(f)

        # Criar 15 Fornecedores (Prestadores de Serviço)
        for _ in range(15):
            subcat = random.choice(subcategorias_fornecedor)
            f = Fornecedor.objects.create(
                categoria='FORNECEDOR',
                subcategoria=subcat,
                status=random.choice(['Sem integração', 'Integrado', 'Pendente'])
            )
            
            FornecedorServico.objects.create(
                fornecedor=f,
                nome_empresa=fake.company(),
                atividade_servico=fake.job()
            )

            # Dados base para todos os tipos de trabalhadores
            trabalhador_data = {
                'fornecedor': f,
                'nome_representante': fake.name()
                # FileFields e ImageFields são deixados em branco
            }
            
            # Criar o tipo de trabalhador específico
            if subcat == 'CLT':
                TrabalhadorCLT.objects.create(**trabalhador_data, descricao_cargo=fake.job())
            elif subcat == 'PJ':
                PessoaJuridica.objects.create(**trabalhador_data)
            elif subcat == 'MEI':
                MEI.objects.create(**trabalhador_data)
            elif subcat == 'AUTONOMO':
                Autonomo.objects.create(**trabalhador_data)
            elif subcat == 'ASSOCIADO':
                Associado.objects.create(**trabalhador_data)

            fornecedores_list.append(f)

        # --- 5. Integrações (para Fornecedores) ---
        self.stdout.write('Criando Integrações...')
        for f in fornecedores_list:
            if f.status != 'Sem integração':
                data_int = fake.date_between(start_date='-2y', end_date='today')
                validade_meses = random.choice([6, 12, 24])
                # O save() do model Integracao calcula a data_validade
                Integracao.objects.create(
                    fornecedor=f,
                    data_integracao=data_int,
                    validade_meses=validade_meses
                )

        # --- 6. Entradas de Fornecedores/Visitantes ---
        self.stdout.write('Criando Entradas de Fornecedores/Visitantes...')
        for _ in range(50): # Criar 50 registros de entrada
            f = random.choice(fornecedores_list)
            entrada_dt = fake.date_time_between(start_date='-60d', end_date='now', tzinfo=timezone.get_current_timezone())
            status = random.choice(['Em andamento', 'Saiu'])
            saida_dt = None
            if status == 'Saiu':
                saida_dt = entrada_dt + timedelta(hours=random.randint(1, 8))

            EntradaFornecedor.objects.create(
                data=entrada_dt.date(),
                horario_entrada=entrada_dt.time(),
                horario_saida=saida_dt.time() if saida_dt else None,
                base=random.choice(base_list),
                fornecedor=f,
                assinatura_portaria=random.choice(users).get_full_name(),
                status=status,
                setor_destino=random.choice(['TI', 'RH', 'Diretoria', 'Financeiro']),
                responsavel_autorizante=fake.name(),
                modelo_veiculo=random.choice(['Carro', 'Moto', 'Caminhão', '']) if f.categoria == 'FORNECEDOR' else '',
                placa_veiculo=fake.license_plate() if random.choice([True, False]) else '',
                usuario_registro=random.choice(users)
            )

        # --- 7. Controle de Chaves ---
        self.stdout.write('Criando Controle de Chaves...')
        for _ in range(40):
            colab = random.choice(colaboradores)
            status = random.choice(['RETIRADO', 'DEVOLVIDO'])
            saida_dt = fake.date_time_between(start_date='-60d', end_date='now', tzinfo=timezone.get_current_timezone())
            devolucao_dt = None
            if status == 'DEVOLVIDO':
                devolucao_dt = saida_dt + timedelta(hours=random.randint(1, 8), minutes=random.randint(0, 59))

            ControleChaves.objects.create(
                base=random.choice(base_list),
                matricula_recebendo=colab.matricula,
                colaborador_recebendo=colab.nome,
                departamento=colab.departamento,
                chave=random.choice(chaves),
                data_saida=saida_dt,
                # Devolução
                matricula_devolveu=colab.matricula if status == 'DEVOLVIDO' else None,
                colaborador_devolveu=colab.nome if status == 'DEVOLVIDO' else None,
                data_devolucao=devolucao_dt,
                situacao=status
                # fotos em branco
            )

        # --- 8. Ocorrências de Crachá ---
        self.stdout.write('Criando Ocorrências de Crachá...')
        for _ in range(30):
            colab = random.choice(colaboradores)
            EsquecimentoCRACHA.objects.create(
                matricula=colab.matricula,
                colaborador=colab.nome,
                departamento=colab.departamento,
                data=fake.date_between(start_date='-60d', end_date='today'),
                motivo=fake.sentence(nb_words=8)
            )

        # --- 9. Ocorrências do Livro ---
        self.stdout.write('Criando Ocorrências do Livro...')
        for _ in range(50):
            Ocorrencia.objects.create(
                base=random.choice(base_list),
                data=fake.date_between(start_date='-60d', end_date='today'),
                ocorrencia=fake.text(max_nb_chars=200),
                usuario=random.choice(users)
            )

        # --- 10. Log de Atividades (Admin) ---
        self.stdout.write('Criando Logs de Atividade...')
        for _ in range(100):
            ActivityLog.objects.create(
                user=random.choice(users),
                action=fake.sentence(nb_words=6),
                timestamp=fake.date_time_between(start_date='-60d', end_date='now', tzinfo=timezone.get_current_timezone())
            )