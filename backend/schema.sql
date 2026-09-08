-- Rode este script no SQL Editor do Supabase (ou via psql)

create table if not exists notes (
  id text primary key,
  area text not null,
  title text not null,
  body text not null,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table if not exists relations (
  id text primary key,
  note_a text not null references notes(id) on delete cascade,
  note_b text not null references notes(id) on delete cascade
);

-- ================= NOTAS INICIAIS =================
insert into notes (id, area, title, body) values
('n1',  'meta',        'Zago',              'Adams Willians Alencar Zago, 47 anos (nasc. 23/04/1979), brasileiro, casado. Coordenador de Soluções e Inovação em TI no Grupo Maqnelson, Uberlândia-MG.'),
('n2',  'metas',       'Financeiro',        'Curto prazo: organizar a vida financeira.'),
('n3',  'metas',       'Impressão 3D',      'Curto prazo: gerar renda extra com produtos impressos em 3D.'),
('n4',  'metas',       'Terrenos',          'Curto prazo: vender dois terrenos em Tupaciguara.'),
('n5',  'metas',       'Longo Prazo',       'Ser promovido, conseguir um salário muito bom e, em 10 anos, aposentar vivendo de soluções próprias como empreendedor.'),
('n6',  'trabalho',    'Maqnelson',         'Coordenador de Soluções e Inovação em TI no Grupo Maqnelson. Foco total em liderar a transformação digital com IA e construir uma esteira de CI/CD com agentes virtuais além dos devs do time.'),
('n7',  'projetos',    'Transf. Digital',   'Liderar a transformação digital do Grupo Maqnelson.'),
('n8',  'projetos',    'Bambu Lab A1',      'Transformar a impressora 3D Bambu Lab A1 em uma fonte de renda.'),
('n9',  'projetos',    'Crossfit',          'Retornar ao Crossfit e gerar o hábito.'),
('n10', 'projetos',    'Beach Tennis',      'Treinar beach tennis.'),
('n11', 'projetos',    'Tênis',             'Jogar mais tênis.'),
('n12', 'projetos',    'Pós em IA',         'Terminar a pós-graduação em IA para lideranças.'),
('n13', 'projetos',    'Vida Financeira',   'Equilibrar a vida financeira.'),
('n14', 'financas',    'Dívidas & Reserva', 'Pagar dívidas, quitar o apartamento e construir reserva de emergência.'),
('n15', 'aprendizado', 'Pós IA',            'Cursando pós-graduação em IA, gestão de agentes e IA para produtividade e liderança.'),
('n16', 'aprendizado', 'Rápido e Devagar',  'Lendo ''Rápido e Devagar: Duas Formas de Pensar'', de Daniel Kahneman.'),
('n17', 'aprendizado', 'Outlive',           'Próxima leitura: ''Outlive'', de Peter Attia.'),
('n18', 'saude',       'Hábito Crossfit',   'Retomar o Crossfit como hábito consistente.'),
('n19', 'saude',       'Saúde Mental',      'Cuidar da saúde mental — sentindo falta de foco.'),
('n20', 'saude',       'Pressão Alta',      'Pressão arterial um pouco alta — atenção necessária.'),
('n21', 'saude',       'Rotina de Exercícios', 'Melhorar a rotina de exercícios: caminhada, pedalada, Crossfit, tênis e beach tennis.'),
('n22', 'relacoes',    'Jesebel',           'Esposa, fisioterapeuta. Base estrutural da vida do Zago.'),
('n23', 'relacoes',    'Davi & Giovanna',   'Filhos: Davi (24 anos) e Giovanna (10 anos).'),
('n24', 'relacoes',    'Tia Solange',       'Tia Solange — como uma mãe.')
on conflict (id) do nothing;

-- ================= RELAÇÕES INICIAIS =================
insert into relations (id, note_a, note_b) values
('r1','n1','n6'), ('r2','n1','n5'), ('r3','n1','n22'), ('r4','n1','n23'), ('r5','n1','n24'),
('r6','n5','n6'), ('r7','n5','n7'), ('r8','n5','n2'),
('r9','n2','n14'), ('r10','n2','n13'), ('r11','n2','n4'),
('r12','n3','n8'),
('r13','n6','n7'), ('r14','n6','n15'),
('r15','n7','n15'),
('r16','n12','n15'),
('r17','n9','n18'), ('r18','n9','n21'),
('r19','n10','n21'), ('r20','n11','n21'),
('r21','n13','n14'),
('r22','n19','n21'), ('r23','n19','n1'),
('r24','n20','n21'), ('r25','n20','n19'),
('r26','n16','n15'), ('r27','n16','n19'),
('r28','n17','n15'), ('r29','n17','n21'),
('r30','n22','n23')
on conflict (id) do nothing;
