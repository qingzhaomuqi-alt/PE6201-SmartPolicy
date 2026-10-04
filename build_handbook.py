"""Build the expanded synthetic handbook and the website's matching policy records.
All supplementary rules are fictional design choices. Original numerical limits are retained.
Run with Python + reportlab. Outputs are deterministic except PDF internal timestamps.
"""
import json
from pathlib import Path
from xml.sax.saxutils import escape
import reportlab
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
ROOT=Path(__file__).resolve().parent
VERSION='2026-10-expanded-demo'
original=json.loads((ROOT/'handbook_base_policies.json').read_text())
# Headings, processes and examples supplement the retained summary clause.
extras={
'meal':[
('Scope and approval','The meal allowance applies to approved office overtime after 20:00. Obtain manager approval before the overtime session and record the work date, end time and business reason. Working late alone does not establish reimbursement eligibility. This allowance does not define overtime wages or compensatory leave.'),
('Evidence and submission','Keep an itemised receipt showing the purchase date, items and total. Submit one evening meal claim with the approval record within 30 calendar days. Identify any personal or alcohol items separately; these items are excluded. Do not split one meal into several claims to bypass the cap.'),
('Limits and examples','The standard maximum is SGD 25 for one eligible evening meal. A SGD 50 dinner does not create a SGD 50 entitlement. The reimbursable portion remains subject to the cap and Finance review. A meal and an eligible taxi trip may be submitted as distinct expense items; each must meet its own conditions.'),
('Missing evidence or uncertainty','For a missing receipt, follow the expense declaration process on the claim-deadlines page. A declaration is not automatic approval. Send unclear eligibility, late claims and exception requests to the manager and Finance. The assistant only explains the recorded policy.')],
'taxi':[
('Time and journey conditions','The rule says after 22:00, not at or after 22:00. Finishing at exactly 22:00 does not by itself satisfy this condition. Approved overtime before 22:00 does not create a late-transport entitlement under this handbook. The covered journey is from the office to the employee\'s home.'),
('Booking and evidence','Record the overtime approval, office departure time, origin and home destination. Keep the taxi receipt with the date and amount. Submit the trip as a transport item in the expense portal within 30 calendar days. A late-night meal receipt is not evidence of a taxi fare.'),
('Exclusions and exceptions','Personal detours, leisure trips and trips starting away from the office are outside this standard clause. Public transport fares, mileage for a personal car and alternative pickup locations are not defined here. Finance must review an exception before any entitlement is asserted.'),
('Worked example','A trip home after approved overtime ending at 22:30 may meet the timing condition if the other requirements are met. A trip after work ending at 21:00 does not meet the late-transport timing condition. The assistant must not convert either example into final approval.')],
'hotel':[
('Before booking','Use an approved business itinerary and record destination, travel dates and the business purpose. Compare the room rate before tax with the SGD 180 nightly cap. If a rate exceeds the cap, obtain written Finance approval before reserving the room.'),
('Claim materials','Submit the hotel invoice, stay dates and proof of business travel approval. Identify taxes separately from the pre-tax room rate. Keep evidence of any approved above-cap rate. The general 30-calendar-day claim deadline also applies to accommodation submissions.'),
('Personal costs and changes','Personal upgrades, extra leisure nights and another person\'s accommodation are outside the standard business-travel allowance. Send cancellation fees, changed itineraries and mixed personal/business stays to Finance for review. This handbook does not define a separate reimbursement entitlement for these items.'),
('Example and escalation','For a room rate of SGD 220 per night before tax, seek approval before booking; the SGD 180 cap is not permission to book any price and automatically recover the difference. Finance decides documented exceptions. The assistant can identify the cap but cannot authorise a hotel reservation.')],
'flight':[
('Reservation route','Use the approved travel portal and include the business purpose, destination, dates and cost centre. Standard bookings are economy class. Obtain written director approval before booking business class; a manager\'s general travel approval does not replace this requirement.'),
('Documents and claims','Keep the itinerary, booking confirmation, fare invoice and approval trail. Finance may request supporting travel evidence when reviewing the claim. Enter flight costs separately from hotel and ground transport costs so each policy can be checked.'),
('Personal additions','A personally chosen cabin upgrade is not reimbursable under the standard rule. Personal itinerary extensions and companion fares must be separated from business costs. The handbook does not set an automatic allowance for baggage, lounge access, seat selection or cancellation fees.'),
('Changes and exceptions','For a route change, urgent rebooking or cancellation, notify the approving manager and Finance and keep the reason and revised booking evidence. Approval of the original itinerary does not automatically approve a higher cabin class. Ask for written review when a change falls outside the recorded policy.')],
'claim':[
('Submission workflow','Create a separate expense item for each type of cost. Include the expense date, business purpose, amount, receipt and approving manager. Attach the relevant exception approval when the standard cap or route was not followed. Submit within 30 calendar days of the expense date.'),
('Receipts and declarations','An itemised receipt should identify the supplier, date, items and total. If a receipt is missing, provide a signed declaration explaining the loss and the expense details. Finance reviews the declaration and may request additional evidence. A declaration does not guarantee approval.'),
('Review and corrections','The manager reviews business necessity; Finance checks documentation and policy limits. Returned claims should be corrected with the missing information rather than duplicated as new claims. Do not submit the same purchase twice or claim a personal cost as a business item.'),
('Late claims and payment','Explain any late submission and seek Finance review. This handbook does not guarantee a payment date or approve late claims automatically. Preserve the written outcome with the claim record. The assistant cannot submit, amend, approve or pay a claim on the employee\'s behalf.')],
'annual':[
('Planning and request','Full-time employees have 18 days of annual leave per calendar year under this fictional rule. Enter requested dates in the HR portal at least 7 calendar days before planned leave and seek manager approval. Check team coverage before committing to personal bookings.'),
('Approval and handover','Provide a short coverage plan for time-sensitive work. Leave is approved only when the manager records approval through the HR process. An application, calendar invitation or assistant answer is not an approval. Inform relevant colleagues of the approved absence.'),
('Changes and balances','For changed dates or cancellation, update the request and ask the manager to confirm the revised arrangement. Use the HR portal for the recorded leave balance; this demo cannot see an employee\'s actual balance. Pro-rating, carry-over, encashment and negative balances are not specified here.'),
('Other leave types','Parental, maternity, paternity, childcare and unpaid leave are not defined by the annual-leave clause. Do not treat the 18-day annual allowance as an answer to those questions. HR must confirm the applicable separate policy and the employee\'s circumstances.')],
'sick':[
('Notification','Notify the manager as soon as possible when illness prevents attendance. State the expected absence without sending unnecessary medical detail to the whole team. The fictional annual outpatient sick-leave allowance for full-time employees is 14 days.'),
('Medical certificate','Upload a medical certificate to the HR portal within 2 working days. Keep the certificate through the approved HR process rather than posting it in a public channel or entering it into this demonstration. Inform HR if timely upload is not possible.'),
('Return and follow-up','Update the manager if the expected return date changes. HR reviews the absence record and supporting certificate. The assistant cannot confirm an employee\'s remaining sick-leave balance, assess medical fitness or issue a medical certificate.'),
('Scope boundaries','Hospitalisation leave, long-term illness arrangements, insurance benefits and treatment reimbursements are not specified by this outpatient allowance. Ask HR for the applicable separate documents. A request about these topics must not be answered as though all illness-related benefits are limited to 14 days.')],
'remote':[
('Weekly arrangement','Eligible employees may request up to 2 remote-work days per week. Agree dates, working availability and task coverage with the manager in advance. Client-facing work may require office attendance, even when the weekly remote limit has not been used.'),
('Communication and equipment','Remain reachable during agreed working periods and use company-approved accounts and equipment. Keep work documents in approved systems. Do not send confidential files to a personal email account to make remote access easier.'),
('Overseas requests','Working from another country requires HR and security approval before travel or the work arrangement begins. A domestic remote-work approval does not include overseas permission. Provide proposed location, dates and the business reason through the approved request process.'),
('Limits and changes','The handbook does not promise a right to work remotely, flexible hours, an internet allowance or permanent work from overseas. Notify the manager of changed arrangements. HR and security review exceptions; the assistant cannot approve them.')],
'probation':[
('Starting period','The standard fictional probation period is 3 months. The manager should communicate role expectations, key tasks and a review schedule at onboarding. Keep the start date and review dates in the HR record rather than relying on a chatbot calculation.'),
('Reviews and feedback','Arrange check-ins to discuss progress, support and training needs. Record specific feedback and agreed actions. A positive informal conversation does not replace written confirmation. Employees can ask the manager and HR to clarify expectations.'),
('Extension process','The manager may extend probation once by up to 3 months and must provide a written reason. HR communicates the extension and any revised review date through the formal process. The assistant cannot extend a period or infer an extension from missing paperwork.'),
('Confirmation and scope','HR communicates confirmation in writing. Passing the expected end date is not, by itself, a confirmation decision in this prototype. Notice periods, termination payments and probation-related statutory rights are not defined here; refer such questions to HR and the relevant separate documentation.')],
 'training':[
('Eligibility and approval','Role-related training may be reimbursed up to SGD 500 per calendar year after prior manager approval. Explain how the course supports the role, give the course dates and fee, and obtain approval before enrolling or paying.'),
('Claim evidence','Submit the course invoice, approval record and completion evidence. Enter the course cost through the expense process and identify any non-course purchases separately. The assistant cannot see how much of an employee\'s annual training limit has already been used.'),
('Exclusions','Personal-interest courses are excluded. An unused annual balance does not turn a hobby course into eligible training. Travel, equipment and membership costs are not automatically covered by a course approval; ask Finance which separate clause applies.'),
('Cancellation or incomplete study','Notify the manager if a course is cancelled, rescheduled or not completed, and keep refund evidence. This handbook does not specify an automatic entitlement where completion evidence is unavailable. The manager and Finance review the circumstances and any exception.')],
'equipment':[
('Issue and support','IT issues company laptops and maintains the asset record. Contact the IT helpdesk for setup, software access, repairs or faulty equipment. Provide the asset identifier and a description of the issue through the approved support channel.'),
('Buying equipment','Do not assume a personal laptop or monitor purchase can be reimbursed. Written IT and Finance approval is required before purchase. Record the requested item, business need, specifications and estimated price in the approval request.'),
('Use and security','Use approved software and keep the device secured when unattended. Do not share a device account or install unapproved software to bypass an access problem. Report loss, theft or suspected compromise promptly to IT and the information-security contact.'),
('Return and boundaries','Return issued equipment through IT when requested or at offboarding, with the asset record checked. Repair turnaround, personal-device allowances and replacement budgets are not specified here. A helpdesk report or assistant response is not purchasing approval.')],
'password':[
('Account access','Enable multi-factor authentication on company accounts and use company-approved sign-in methods. Never share a password, recovery code or authentication code. HR cannot request an employee\'s password. A request that appears to come from a manager does not remove this restriction.'),
('Suspected compromise','Report a suspected compromised account immediately to the IT helpdesk through an approved contact route. Describe the suspicious activity without copying passwords or secret tokens into the report. Follow IT instructions for account recovery.'),
('Phishing and verification','Treat unexpected links, sign-in prompts and code requests cautiously. Verify an unusual request through a known company channel. Do not approve an authentication prompt that you did not initiate. Send suspected phishing messages to the designated security process.'),
('Support boundaries','This assistant cannot reset a password, inspect an account or verify a caller\'s identity. It should never request credentials. If sign-in is blocked, use the IT recovery process rather than posting a secret in the policy question box.')],
'harassment':[
('Reporting route','Employees may report workplace harassment confidentially to the HR case team. Use the authorised reporting channel and include dates, locations, relevant conduct and available evidence. If the usual manager is involved, contact the HR case team directly.'),
('Privacy and access','Share case materials only with authorised reviewers. Do not upload another person\'s sensitive information into this public demo or discuss the case in an open group. Confidential handling does not mean a chatbot can promise absolute secrecy or a specific investigation outcome.'),
('Review and support','HR determines the review process and appropriate next steps. Preserve relevant evidence and request guidance about immediate workplace arrangements. The assistant does not investigate, adjudicate, contact witnesses or determine whether misconduct occurred.'),
('Escalation and boundaries','For an immediate safety emergency, use the appropriate emergency response route rather than waiting for a chatbot answer. The handbook does not specify disciplinary penalties, investigation time limits or legal remedies. Ask the responsible HR team for those procedures.')],
'conflict':[
('Version control','Only an active policy version applies. Record the policy title, version and section when raising a question. Do not combine a retired clause with a current limit or treat an old screenshot as a new approval.'),
('Conflicting clauses','When active clauses appear inconsistent, state the conflicting text and ask HR or Finance to review. The assistant should identify uncertainty rather than choose whichever clause offers the larger benefit. Related policies can apply to separate expense items without necessarily conflicting.'),
('Exceptions and authority','An exception must be documented by the responsible approval owner. The assistant cannot approve a claim, override policy or create an entitlement. A verbal assumption, unanswered request or chatbot response is not a documented exception.'),
('Missing policies','If the handbook has no applicable clause, say that the matter is not specified and ask the responsible team. Overtime wages, compensatory leave and statutory employment entitlements are not established by this demonstration. Do not infer them from an expense allowance.')],
'privacy':[
('Data origin','The handbook and test questions are synthetic and developed with AI assistance for PE6201. They are not NTU rules, a real company handbook or an authoritative summary of employment law. No real employee records were used to construct this collection.'),
('Safe input','Do not enter personal records, salaries, bank numbers, medical documents, credentials or confidential company material. Use fictional examples when testing the assistant. This public demo is designed for generic policy questions, not individual employee case management.'),
('Question handling','The application keeps the current conversation in page memory only and does not save questions to an application database. Refreshing clears the visible session. Hosting services may process routine technical access data; this statement is not a promise that no infrastructure logs exist.'),
('Access and limitations','The public website has no employee authentication or production access controls. It quotes the indexed handbook and does not independently validate real-world policy, identity or eligibility. The Python/Colab submission package is a separate snapshot and must be checked before claiming identical data versions.')]
}
new=[
('onboarding','Onboarding and employee records','New employees complete onboarding through HR and IT before using company systems. Access is granted for the role and recorded in the appropriate team\'s process.',[
('Joining checklist','Confirm the start date, manager, role description and induction schedule with HR. Attend the policy orientation and arrange equipment setup with IT. Read the current handbook and ask the responsible team about unclear requirements.'),
('Information collection','Provide employee documents only through an authorised HR channel. Do not enter identity documents, bank details or home addresses in the public policy assistant. HR specifies what records are required and how they are submitted.'),
('Access and changes','Request accounts and permissions through IT and obtain the relevant owner\'s approval. Tell HR when a role or contact record changes through the approved process. Do not use a colleague\'s account while waiting for access.'),
('Not defined here','Offer-specific salary amounts, stock options, pension contributions, severance, childcare subsidies, employment contract terms, immigration requirements and statutory registration obligations are outside this synthetic handbook. HR must confirm the relevant documents. The assistant cannot verify onboarding completion or grant access.')]),
('attendance','Attendance and work schedules','Follow the work schedule agreed with the manager. Notify the manager promptly about lateness, unexpected absence or a schedule change; recorded approval is required for agreed exceptions.',[
('Daily arrangements','Confirm ordinary working periods, meeting coverage and any shift arrangement with the manager. This handbook does not establish one universal start or finish time for every role. Remote-work approval does not automatically change the agreed schedule.'),
('Lateness and absence','Use the team\'s approved notification route, give an expected arrival or return time and flag urgent work needing coverage. Record approved changes through the relevant attendance or HR process. Avoid sharing sensitive personal details in open channels.'),
('Additional work','Seek manager approval before planned overtime and keep a record of the business need and hours. Meal and taxi claims use their separate timing and receipt requirements. Approval to work additional hours does not establish an overtime wage rate in this handbook.'),
('Boundaries','Break schedules, time-recording calculations, wage deductions and time off in lieu are not specified here. Ask HR and the manager for the relevant authorised terms. The assistant does not interpret time records or decide attendance penalties.')]),
('procurement','Business purchasing and procurement','Request approval before committing company funds. Use the designated purchasing process and document the business need, supplier, quote and approval; an assistant answer is not authority to place an order.',[
('Request preparation','Describe the item or service, estimated total cost, intended use and cost centre. Ask Procurement or Finance which approval owner applies. This handbook does not invent a universal purchasing threshold or an automatic approval amount.'),
('Supplier and order','Use an approved supplier or request supplier review before ordering. Preserve the quote, written approval and order record. Do not divide a purchase into smaller orders to avoid the relevant approval process.'),
('Receipt and invoice','Check delivered goods or services against the order and keep the invoice and delivery evidence. Report mismatches to Procurement and Finance before asserting that payment is due. Handle personal purchases separately from business orders.'),
('Relationship to expenses','Equipment purchases still require IT and Finance approval where that equipment clause applies. Reimbursement after a personal purchase is not a substitute for pre-purchase approval. Approval timelines, supplier terms and payment dates are not fixed by this handbook.')]),
('gifts','Gifts and conflicts of interest','Disclose a potential conflict of interest and seek compliance or manager review before accepting a business gift or hospitality that could influence a decision. No gift-value threshold is defined in this synthetic handbook.',[
('Disclosure','Identify the business relationship, proposed gift or event and any purchasing or hiring decision involved. Use the approved compliance disclosure route. Do not assume that a low monetary value eliminates a conflict.'),
('Pending review','Do not promise favourable treatment, exchange an approval for a benefit or accept an item while the required review is unresolved. Document the reviewer\'s response. A manager\'s informal comment is not a recorded compliance decision.'),
('Related-party decisions','Tell the decision owner if a supplier or candidate has a personal relationship with you. The responsible team determines whether reassignment, additional review or another control is needed. The assistant cannot clear a conflict or certify a transaction.'),
('Limits','Specific gift caps, disciplinary actions and external legal requirements are not supplied here. Ask the authorised compliance contact for the applicable policy. Avoid posting another person\'s private details in the public demo.')]),
('incident','Information security and incident reporting','Use approved systems for company information. Report lost devices, suspected data exposure or suspicious system activity promptly to IT or the information-security contact, without posting the affected data in the policy assistant.',[
('Routine handling','Store work files in approved locations and share them only with authorised recipients. Verify access permissions before sending a link. Do not move confidential documents to a personal cloud account or a public website for convenience.'),
('Report details','Provide the time, affected system or device, type of event and immediate observations through the secure reporting channel. Do not include passwords or unnecessary copies of sensitive records. Preserve relevant evidence for the response team.'),
('Response authority','Follow the designated response team\'s instructions. Do not independently publish incident details, contact affected people or claim that an investigation is complete. Account compromise also invokes the account-security reporting process.'),
('Boundaries','Classification schemes, data-retention periods and external breach-notification deadlines are not established here. The responsible team must confirm them. The assistant gives handbook information and cannot investigate, delete system logs or certify recovery.')])]
records=[]
for d in original:
 d=dict(d);d['summary']=d['text'];d['clauses']=[{'heading':'Policy summary','text':d['summary']}]+[{'heading':h,'text':t} for h,t in extras[d['id']]];records.append(d)
for ident,title,summary,details in new:
 records.append({'id':ident,'title':title,'summary':summary,'active':True,'clauses':[{'heading':'Policy summary','text':summary}]+[{'heading':h,'text':t} for h,t in details]})
for i,d in enumerate(records):
 d['page']=i+3;d['version']=VERSION;d['text']='\n\n'.join(c['heading']+'\n'+c['text'] for c in d['clauses'])
(ROOT/'dist/policies.json').write_text(json.dumps(records,indent=2))
fonts=Path(reportlab.__file__).resolve().parent/'fonts'
for name,f in [('Book','Vera.ttf'),('BookBold','VeraBd.ttf')]:pdfmetrics.registerFont(TTFont(name,str(fonts/f)))
c=canvas.Canvas(str(ROOT/'dist/Demo_Company_Policy.pdf'),pagesize=A4);W,H=A4
c.setTitle('SmartPolicy Expanded Fictional Employee Handbook');c.setAuthor('SmartPolicy - AI-assisted PE6201 prototype')
body=ParagraphStyle('body',fontName='Book',fontSize=10.4,leading=15,textColor='#29364c')
head=ParagraphStyle('head',fontName='BookBold',fontSize=11,leading=16,textColor='#234abf')
used=[]
def para(text,y,style=body):
 p=Paragraph(escape(text),style);_,height=p.wrap(W-100,H);p.drawOn(c,50,y-height);return y-height-10

def frame(number,section):
 c.setFillColorRGB(.07,.13,.24);c.rect(0,H-65,W,65,fill=1,stroke=0);c.setFillColorRGB(1,1,1);c.setFont('BookBold',13);c.drawString(50,H-37,'SmartPolicy');c.setFont('Book',9);c.drawRightString(W-50,H-37,VERSION)
 c.setFillColorRGB(.35,.4,.5);c.setFont('Book',8);c.drawString(50,40,'FICTIONAL POLICIES | COURSE DEMO | NOT EMPLOYMENT ADVICE');c.drawRightString(W-50,40,str(number));c.bookmarkPage(section)
def title(t):return para(t,H-97,ParagraphStyle('title',fontName='BookBold',fontSize=21,leading=27,textColor='#142744'))
frame(1,'introduction');y=title('Employee handbook');y=para('Expanded demonstration edition',y,head);y=para('Demo Company | 20 policy chapters | 3 October 2026',y)
for h,t in [
('Purpose and origin','This handbook is an AI-assisted synthetic dataset for the PE6201 SmartPolicy project. It was written to demonstrate policy lookup and source citation. It is not a document issued by NTU, a real company or a government authority. All policy limits and supplementary procedures are fictional design choices.'),
('How to read it','Use the table of contents to find a chapter. Each chapter presents a retained policy summary plus process details, evidence requirements and limits. Page numbers in the assistant refer to the physical pages in this PDF. Confirm any real employment matter with the relevant authorised organisation.'),
('Approval and missing information','The assistant explains recorded clauses; it does not authorise spending, approve leave, investigate complaints or determine individual eligibility. Missing rules must be identified as unspecified. Overtime wages, time off in lieu and statutory employment entitlements are intentionally not established by this handbook.'),
('Version and relationship to earlier work','This expanded website collection replaces the earlier 15 short sections in the public demo. It retains the original numerical limits but adds fictional process details and five chapters. The existing Python/Colab package and earlier evaluation report remain separate snapshots; their results must not be attributed to this new collection without re-evaluation.')]:
 y=para(h,y,head);y=para(t,y)
used.append(y);c.showPage();frame(2,'contents');y=title('Contents')
for d in records:
 c.setFillColorRGB(.15,.2,.3);c.setFont('Book',10.5);c.drawString(50,y-14,d['title']);c.drawRightString(W-50,y-14,str(d['page']));c.linkRect('',d['id'],(50,y-21,W-50,y),relative=0,thickness=0);y-=27
used.append(y);c.showPage()
for d in records:
 frame(d['page'],d['id']);c.addOutlineEntry(d['title'],d['id']);y=title(d['title'])
 for clause in d['clauses']:
  y=para(clause['heading'],y,head);y=para(clause['text'],y)
 if y<65:raise RuntimeError('Page overflow: '+d['id']+' '+str(y))
 used.append(y);c.showPage()
c.save();print('Created',len(records),'chapters;',len(used),'pages; lowest text boundary',round(min(used),1))
