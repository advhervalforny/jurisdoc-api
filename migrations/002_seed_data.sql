-- ============================================================================
-- JURISDOC - DADOS DE SEED
-- Sistema Jurídico Inteligente AI-First
-- ============================================================================
-- Execute após o schema inicial (001_initial_schema.sql)
-- ============================================================================

-- ============================================================================
-- FONTES JURÍDICAS INICIAIS
-- ============================================================================
-- Fontes básicas para começar a usar o sistema
-- Embeddings serão gerados posteriormente via código

-- Constituição Federal
INSERT INTO legal_sources (source_type, reference, excerpt) VALUES
('constituicao', 'CF, art. 5º, caput', 'Todos são iguais perante a lei, sem distinção de qualquer natureza, garantindo-se aos brasileiros e aos estrangeiros residentes no País a inviolabilidade do direito à vida, à liberdade, à igualdade, à segurança e à propriedade.'),
('constituicao', 'CF, art. 5º, XXXV', 'A lei não excluirá da apreciação do Poder Judiciário lesão ou ameaça a direito.'),
('constituicao', 'CF, art. 5º, LIV', 'Ninguém será privado da liberdade ou de seus bens sem o devido processo legal.'),
('constituicao', 'CF, art. 5º, LV', 'Aos litigantes, em processo judicial ou administrativo, e aos acusados em geral são assegurados o contraditório e ampla defesa, com os meios e recursos a ela inerentes.'),
('constituicao', 'CF, art. 5º, X', 'São invioláveis a intimidade, a vida privada, a honra e a imagem das pessoas, assegurado o direito a indenização pelo dano material ou moral decorrente de sua violação.')
ON CONFLICT DO NOTHING;

-- Código de Processo Civil
INSERT INTO legal_sources (source_type, reference, excerpt) VALUES
('lei', 'CPC, art. 319', 'A petição inicial indicará: I - o juízo a que é dirigida; II - os nomes, os prenomes, o estado civil, a existência de união estável, a profissão, o número de inscrição no Cadastro de Pessoas Físicas ou no Cadastro Nacional da Pessoa Jurídica, o endereço eletrônico, o domicílio e a residência do autor e do réu; III - o fato e os fundamentos jurídicos do pedido; IV - o pedido com as suas especificações; V - o valor da causa; VI - as provas com que o autor pretende demonstrar a verdade dos fatos alegados; VII - a opção do autor pela realização ou não de audiência de conciliação ou de mediação.'),
('lei', 'CPC, art. 320', 'A petição inicial será instruída com os documentos indispensáveis à propositura da ação.'),
('lei', 'CPC, art. 335', 'O réu poderá oferecer contestação, por petição, no prazo de 15 (quinze) dias, cujo termo inicial será a data: I - da audiência de conciliação ou de mediação, ou da última sessão de conciliação, quando qualquer parte não comparecer ou, comparecendo, não houver autocomposição; II - do protocolo do pedido de cancelamento da audiência de conciliação ou de mediação apresentado pelo réu, quando ocorrer a hipótese do art. 334, § 4º, inciso I; III - prevista no art. 231, de acordo com o modo como foi feita a citação, nos demais casos.'),
('lei', 'CPC, art. 336', 'Incumbe ao réu alegar, na contestação, toda a matéria de defesa, expondo as razões de fato e de direito com que impugna o pedido do autor e especificando as provas que pretende produzir.'),
('lei', 'CPC, art. 337', 'Incumbe ao réu, antes de discutir o mérito, alegar: I - inexistência ou nulidade da citação; II - incompetência absoluta e relativa; III - incorreção do valor da causa; IV - inépcia da petição inicial; V - perempção; VI - litispendência; VII - coisa julgada; VIII - conexão; IX - incapacidade da parte, defeito de representação ou falta de autorização; X - convenção de arbitragem; XI - ausência de legitimidade ou de interesse processual; XII - falta de caução ou de outra prestação que a lei exige como preliminar; XIII - indevida concessão do benefício de gratuidade de justiça.'),
('lei', 'CPC, art. 351', 'Se o réu alegar fato impeditivo, modificativo ou extintivo do direito do autor, este será ouvido no prazo de 15 (quinze) dias, permitindo-lhe o juiz a produção de prova.'),
('lei', 'CPC, art. 1.009', 'Da sentença cabe apelação. § 1º As questões resolvidas na fase de conhecimento, se a decisão a seu respeito não comportar agravo de instrumento, não são cobertas pela preclusão e devem ser suscitadas em preliminar de apelação, eventualmente interposta contra a decisão final, ou nas contrarrazões. § 2º Se as questões referidas no § 1º forem suscitadas em contrarrazões, o recorrente será intimado para, em 15 (quinze) dias, manifestar-se a respeito delas. § 3º O disposto no caput deste artigo aplica-se mesmo quando as questões mencionadas no art. 1.015 integrarem capítulo da sentença.')
ON CONFLICT DO NOTHING;

-- Código Civil
INSERT INTO legal_sources (source_type, reference, excerpt) VALUES
('lei', 'CC, art. 186', 'Aquele que, por ação ou omissão voluntária, negligência ou imprudência, violar direito e causar dano a outrem, ainda que exclusivamente moral, comete ato ilícito.'),
('lei', 'CC, art. 187', 'Também comete ato ilícito o titular de um direito que, ao exercê-lo, excede manifestamente os limites impostos pelo seu fim econômico ou social, pela boa-fé ou pelos bons costumes.'),
('lei', 'CC, art. 927', 'Aquele que, por ato ilícito (arts. 186 e 187), causar dano a outrem, fica obrigado a repará-lo. Parágrafo único. Haverá obrigação de reparar o dano, independentemente de culpa, nos casos especificados em lei, ou quando a atividade normalmente desenvolvida pelo autor do dano implicar, por sua natureza, risco para os direitos de outrem.'),
('lei', 'CC, art. 944', 'A indenização mede-se pela extensão do dano. Parágrafo único. Se houver excessiva desproporção entre a gravidade da culpa e o dano, poderá o juiz reduzir, eqüitativamente, a indenização.')
ON CONFLICT DO NOTHING;

-- Código de Defesa do Consumidor
INSERT INTO legal_sources (source_type, reference, excerpt) VALUES
('lei', 'CDC, art. 6º, VI', 'São direitos básicos do consumidor: VI - a efetiva prevenção e reparação de danos patrimoniais e morais, individuais, coletivos e difusos.'),
('lei', 'CDC, art. 14', 'O fornecedor de serviços responde, independentemente da existência de culpa, pela reparação dos danos causados aos consumidores por defeitos relativos à prestação dos serviços, bem como por informações insuficientes ou inadequadas sobre sua fruição e riscos.'),
('lei', 'CDC, art. 43, §2º', 'A abertura de cadastro, ficha, registro e dados pessoais e de consumo deverá ser comunicada por escrito ao consumidor, quando não solicitada por ele.'),
('lei', 'CDC, art. 43, §3º', 'O consumidor, sempre que encontrar inexatidão nos seus dados e cadastros, poderá exigir sua imediata correção, devendo o arquivista, no prazo de cinco dias úteis, comunicar a alteração aos eventuais destinatários das informações incorretas.')
ON CONFLICT DO NOTHING;

-- Código de Processo Penal
INSERT INTO legal_sources (source_type, reference, excerpt) VALUES
('lei', 'CPP, art. 41', 'A denúncia ou queixa conterá a exposição do fato criminoso, com todas as suas circunstâncias, a qualificação do acusado ou esclarecimentos pelos quais se possa identificá-lo, a classificação do crime e, quando necessário, o rol das testemunhas.'),
('lei', 'CPP, art. 396', 'Nos procedimentos ordinário e sumário, oferecida a denúncia ou queixa, o juiz, se não a rejeitar liminarmente, recebê-la-á e ordenará a citação do acusado para responder à acusação, por escrito, no prazo de 10 (dez) dias.'),
('lei', 'CPP, art. 396-A', 'Na resposta, o acusado poderá argüir preliminares e alegar tudo o que interesse à sua defesa, oferecer documentos e justificações, especificar as provas pretendidas e arrolar testemunhas, qualificando-as e requerendo sua intimação, quando necessário.')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- JURISPRUDÊNCIA INICIAL
-- ============================================================================

INSERT INTO legal_sources (source_type, reference, excerpt) VALUES
('jurisprudencia', 'STJ, Súmula 385', 'Da anotação irregular em cadastro de proteção ao crédito, não cabe indenização por dano moral, quando preexistente legítima inscrição, ressalvado o direito ao cancelamento.'),
('jurisprudencia', 'STJ, Súmula 403', 'Independe de prova do prejuízo a indenização pela publicação não autorizada de imagem de pessoa com fins econômicos ou comerciais.'),
('jurisprudencia', 'STJ, Súmula 227', 'A pessoa jurídica pode sofrer dano moral.'),
('jurisprudencia', 'STJ, REsp 1.061.134/RS', 'A inscrição indevida em cadastro de inadimplentes configura dano moral in re ipsa, dispensada a prova do prejuízo.'),
('jurisprudencia', 'STF, Súmula Vinculante 25', 'É ilícita a prisão civil de depositário infiel, qualquer que seja a modalidade de depósito.')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- VERIFICAÇÃO
-- ============================================================================

-- Verificar contagem de fontes por tipo
-- SELECT source_type, COUNT(*) FROM legal_sources GROUP BY source_type ORDER BY source_type;
